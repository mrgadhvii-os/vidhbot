FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set environment variable for production
ENV ENVIRONMENT=production

# Expose the port that the app will run on
EXPOSE 8080

CMD ["python", "bot.py"] 
