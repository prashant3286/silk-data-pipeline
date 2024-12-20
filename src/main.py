import logging
from pymongo import MongoClient
from datetime import datetime

from .config.settings import settings
from .clients.qualys import QualysClient
from .clients.crowdstrike import CrowdstrikeClient
from .services.deduplication import HostDeduplicator
from .services.normalization import HostNormalizer

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
        
        logger.info("Fetching hosts from Crowdstrike")
        crowdstrike_hosts = crowdstrike_client.get_normalized_hosts()
        
        # Combine hosts from both sources
        all_hosts = qualys_hosts + crowdstrike_hosts
        
        # Normalize hosts
        normalized_hosts = [
            HostNormalizer.normalize_host_data(host.raw_data) 
            for host in all_hosts
        ]
        
        # Deduplicate hosts
        deduplicator = HostDeduplicator()
        deduplicated_hosts = deduplicator.deduplicate_hosts(all_hosts)
        
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
    
    except Exception as e:
        logger.error(f"Error in host processing pipeline: {e}")

if __name__ == "__main__":
    fetch_and_process_hosts()