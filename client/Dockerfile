# Build stage
FROM node:20-alpine AS build

# Set up working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./
# ./ (current directory in destination)

# Install depedencies
RUN npm ci
# clean install
# deletes node modules first
# installs from package-lock.json

# Copy source code
COPY . .

# Build the app
RUN npm run build


# Production stage
FROM nginx:alpine

# Copy built files to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]