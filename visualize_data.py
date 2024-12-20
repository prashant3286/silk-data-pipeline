import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import seaborn as sns
from typing import List
from src.models.host import Host

class HostDataVisualizer:
    @staticmethod
    def visualize_host_data(hosts: List[Host], output_dir: str = '.'):
        """
        Create comprehensive visualizations for host data
        
        :param hosts: List of Host objects
        :param output_dir: Directory to save visualization images
        """
        # Convert hosts to DataFrame
        df = pd.DataFrame([host.to_dict() for host in hosts])
        
        # Set up the visualization
        plt.figure(figsize=(15, 10))
        plt.suptitle('Host Data Visualization', fontsize=16)
        
        # Subplot 1: OS Distribution
        plt.subplot(2, 2, 1)
        os_counts = df['operating_system'].value_counts()
        os_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('Host Distribution by Operating System')
        plt.ylabel('')
        
        # Subplot 2: Host Age Distribution
        plt.subplot(2, 2, 2)
        df['days_since_last_seen'] = (datetime.now() - pd.to_datetime(df['last_seen'])).dt.days
        plt.hist(df['days_since_last_seen'], bins=20, edgecolor='black')
        plt.title('Host Age Distribution')
        plt.xlabel('Days Since Last Seen')
        plt.ylabel('Number of Hosts')
        
        # Subplot 3: Vulnerability Count Heatmap
        plt.subplot(2, 2, 3)
        plt.title('Vulnerability Count Heatmap')
        vulnerability_pivot = df.pivot_table(
            values='vulnerability_count', 
            index='operating_system', 
            aggfunc='mean'
        )
        sns.heatmap(vulnerability_pivot, annot=True, cmap='YlOrRd')
        
        # Subplot 4: Active vs Inactive Hosts
        plt.subplot(2, 2, 4)
        cutoff_date = datetime.now() - timedelta(days=30)
        df['host_status'] = df['last_seen'].apply(
            lambda x: 'Active' if pd.to_datetime(x) > cutoff_date else 'Inactive'
        )
        df['host_status'].value_counts().plot(kind='bar')
        plt.title('Active vs Inactive Hosts')
        plt.xlabel('Host Status')
        plt.ylabel('Number of Hosts')
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(f'{output_dir}/host_data_visualization.png')
        plt.close()

# Example usage
if __name__ == "__main__":
    from src.main import fetch_and_process_hosts
    
    # Fetch hosts
    hosts = fetch_and_process_hosts()
    
    # Visualize
    HostDataVisualizer.visualize_host_data(hosts)