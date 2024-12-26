import logging
from pymongo import MongoClient
from datetime import datetime

from .config.settings import settings
from .clients.qualys import QualysClient
from .clients.crowdstrike import CrowdstrikeClient
from .services.deduplication import HostDeduplicator
from .services.normalization import HostNormalizer
from .models.host import Host 

def setup_logging():
    """
    Configure logging for the application
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def connect_to_mongodb():
    """
    Establish MongoDB connection
    
    :return: MongoDB database connection
    """
    try:
        client = MongoClient(settings.MONGODB_URI)
        db = client[settings.DATABASE_NAME]
        return db
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise

def fetch_and_process_hosts():
    """
    Main data pipeline: fetch, normalize, and deduplicate hosts
    
    :return: List of deduplicated Host objects
    """
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize clients
        qualys_client = QualysClient()
        crowdstrike_client = CrowdstrikeClient()
        
        # Fetch hosts from both sources
        logger.info("Fetching hosts from Qualys")
        qualys_hosts = qualys_client.get_normalized_hosts()
        logger.info(f"Fetched {len(qualys_hosts)} hosts from Qualys")
        
        logger.info("Fetching hosts from Crowdstrike")
        crowdstrike_hosts = crowdstrike_client.get_normalized_hosts()
        logger.info(f"Fetched {len(crowdstrike_hosts)} hosts from Crowdstrike")
        
        # Combine hosts from both sources
        all_hosts = qualys_hosts + crowdstrike_hosts
        
        
        # Normalize hosts (if not done within the client already)
        normalized_hosts = []
        for host in all_hosts:
            logger.debug(f"Normalizing host: {host}")
            normalized_host_data = HostNormalizer.normalize_host_data(host.raw_data)
            # Filter out unwanted keys
            allowed_keys = {field.name for field in Host.__dataclass_fields__.values()}
            filtered_data = {k: v for k, v in normalized_host_data.items() if k in allowed_keys}
            normalized_hosts.append(Host(**filtered_data))
        
        # Deduplicate hosts
        deduplicator = HostDeduplicator()
        deduplicated_hosts = deduplicator.deduplicate_hosts(normalized_hosts)
        
        # Connect to MongoDB
        db = connect_to_mongodb()
        hosts_collection = db['hosts']
        
        # Store hosts in MongoDB
        for host in deduplicated_hosts:
            host_data = host.to_dict()
            host_data['processed_at'] = datetime.utcnow()
            
            # Upsert based on source system and source ID
            hosts_collection.update_one(
                {
                    'source_system': host.source_system,
                    'source_id': host.source_id
                },
                {'$set': host_data},
                upsert=True
            )
        
        logger.info(f"Processed {len(deduplicated_hosts)} unique hosts")
        return deduplicated_hosts
    
    except Exception as e:
        logger.error(f"Error in host processing pipeline: {e}")
        logger.exception(e)
        return []

if __name__ == "__main__":
    hosts = fetch_and_process_hosts()