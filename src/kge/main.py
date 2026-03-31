import os
import time
import torch

import pykeen
from pykeen.triples import TriplesFactory
from pykeen.pipeline import pipeline
from pykeen.models import TransE, ComplEx

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

TRAIN_PATH = "artifacts/train.txt"
VALID_PATH  = "artifacts/valid.txt"
TEST_PATH   = "artifacts/test.txt"

tf_train = TriplesFactory.from_path(
    TRAIN_PATH,
    delimiter="\t"
)
tf_valid = TriplesFactory.from_path(
    VALID_PATH,
    delimiter="\t",
    entity_to_id=tf_train.entity_to_id,
    relation_to_id=tf_train.relation_to_id,
)
tf_test = TriplesFactory.from_path(
    TEST_PATH,
    delimiter="\t",
    entity_to_id=tf_train.entity_to_id,
    relation_to_id=tf_train.relation_to_id,
)

print(f" Train : {tf_train.num_triples:>6,} triplets")
print(f" Valid : {tf_valid.num_triples:>6,} triplets")
print(f" Test : {tf_test.num_triples:>6,} triplets")
print(f" Entités : {tf_train.num_entities:,}")
print(f" Relations : {tf_train.num_relations:,}")

EMBEDDING_DIM = 128
EPOCHS        = 200
BATCH_SIZE    = 256
LR            = 1e-3

results_store = {}

model_name = "TransE"

cfg = {
    "model": "TransE",
    "model_kwargs": {
        "embedding_dim": EMBEDDING_DIM,
    },
    "loss": "MarginRankingLoss",
    "color":   "#E74C3C",
}

print(f"\n{'─'*55}")
print(f"  Training : {model_name}")
print(f"{'─'*55}")
t_start = time.time()

result = pipeline(

    training=tf_train,
    validation=tf_valid,
    testing=tf_test,

    model=cfg["model"],
    model_kwargs=cfg["model_kwargs"],

    loss=cfg["loss"],

    optimizer="Adam",
    optimizer_kwargs={"lr": LR},

    negative_sampler="basic",
    negative_sampler_kwargs={
        "num_negs_per_pos":15,
    },

    training_kwargs={
        "num_epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
    },

    stopper="early",
    stopper_kwargs=dict(
        frequency=10,
        patience=5,
    ),

    evaluator="RankBasedEvaluator",
    evaluation_kwargs={
        "batch_size": BATCH_SIZE
    },

    random_seed=42,
    device=device,
)

elapsed = time.time() - t_start
result_data = {
    "pipeline_result": result,
    "elapsed":         elapsed,
}

result = result_data["pipeline_result"]
metrics = result.metric_results.to_flat_dict()
mrr = metrics.get("both.realistic.inverse_harmonic_mean_rank", 0)
hits1 = metrics.get("both.realistic.hits_at_1", 0)
hits3 = metrics.get("both.realistic.hits_at_3", 0)
hits10  = metrics.get("both.realistic.hits_at_10", 0)

print(f"{model_name} entraîné en {result_data["elapsed"]:.0f}s")
print(f"MRR : {mrr:.4f}")
print(f"Hits@1 : {hits1:.4f}")
print(f"Hits@3 : {hits3:.4f}")
print(f"Hits@10 : {hits10:.4f}")

print("---")

result = result_data["pipeline_result"]

save_dir = f"models/kge_{model_name.lower()}"
os.makedirs(save_dir, exist_ok=True)

result.save_to_directory(save_dir)
