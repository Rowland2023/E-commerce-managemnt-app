# Use the official Node.js 18 LTS image
FROM node:18-slim

# Install curl for healthchecks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# ... rest of your file (COPY, RUN npm install, etc.)

# Copy package.json and package-lock.json first
COPY package*.json ./

# Install dependencies (including devDependencies if you use nodemon)
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 3000
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]