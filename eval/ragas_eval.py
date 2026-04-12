from ragas import SingleTurnSample
from ragas import evaluate, EvaluationDataset
from ragas.metrics import Faithfulness, ContextPrecision, ContextRecall
import json
import time
from src.generation.generator import rag
from config import GROQ_MODEL
from langchain_groq import ChatGroq
from ragas.llms import LangchainLLMWrapper

def ragas_eval():
    
    llm = LangchainLLMWrapper(ChatGroq(model=GROQ_MODEL))

    with open("eval/qa_pairs.json", "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)
    
    samples = []
    for pair in qa_pairs:
        answer, retrieved, _ = rag(pair["question"], top_k=2)
        time.sleep(60)  # pause between queries to avoid rate limits
        sample = SingleTurnSample(
            user_input=pair["question"],
            retrieved_contexts=[r.get("text") for r in retrieved],
            response=answer,
            reference=pair["ground_truth"]
        )
        samples.append(sample)

    results = []
    
    dataset = EvaluationDataset(samples=samples)
    results = evaluate(dataset,metrics=[Faithfulness(), ContextPrecision(), ContextRecall()],llm=llm,raise_exceptions=True)
    print(results)

    with open("eval/aspice_eval.json", "w", encoding="utf-8") as f:
        json.dump(results.to_pandas().to_dict(orient="records"), f, indent=2)
    
    print("Saved in current directory as aspice_eval.json")

if __name__ == "__main__":
    ragas_eval()