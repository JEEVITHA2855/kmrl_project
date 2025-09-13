from transformers import pipeline

# 1️⃣ Load summarization model
summarizer = pipeline("summarization")

# 2️⃣ Read the sample document
with open("sample_document.txt", "r") as f:
    text = f.read()

# 3️⃣ Summarize the text
summary = summarizer(text, max_length=50, min_length=20, do_sample=False)[0]['summary_text']

print("Summary:")
print(summary)

# 4️⃣ Alert keywords
alert_keywords = ["risk", "urgent", "safety", "incident"]

# 5️⃣ Detect alerts in summary
alerts = [word for word in alert_keywords if word.lower() in summary.lower()]

if alerts:
    print("\nALERT! Keywords found:", alerts)
else:
    print("\nNo alerts found.")
