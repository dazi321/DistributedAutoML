import argparse
from dml.miners import MinerFactory
from dml.chain.btt_connector import BittensorNetwork
from dml.configs.config import config

def main(config, miner_type):
    """Runs the miner based on configuration."""
    bt_config = config.get_bittensor_config()
    BittensorNetwork.initialize(bt_config)
    config.bittensor_network = BittensorNetwork

    try:
        miner = MinerFactory.get_miner(config, miner_type)
        best_genome = miner.mine()

        print(f"Best genome fitness: {best_genome.fitness.values[0]:.4f}")
        print(f"Baseline accuracy: {miner.baseline_accuracy:.4f}")
        print(f"Improvement over baseline: {best_genome.fitness.values[0] - miner.baseline_accuracy:.4f}")

        return best_genome
    except Exception as e:
        print(f"Error during mining: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Bittensor miner.")
    parser.add_argument("--miner_type", type=str, default="loss", help="Specify miner type (e.g., 'loss', 'simple').")
    
    args = parser.parse_args()
    best_genome = main(config, args.miner_type)
