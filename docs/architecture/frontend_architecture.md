# Frontend Architecture for Agent Provocateur

This document outlines the frontend architecture for Agent Provocateur, including the recommended file structure, technology choices, and implementation guidelines.

## File Structure

The recommended file structure integrates a frontend with the existing backend:

```
agent_provocateur/
├── backend/                     # Backend code (renamed from src)
│   └── agent_provocateur/       # Python package
├── docs/                        # Documentation
│   ├── document_types.md
│   ├── frontend_architecture.md
│   └── xml_verification.md
├── examples/                    # Example files
│   ├── sample.xml
│   └── sample_rules.json
├── frontend/                    # Frontend code
│   ├── public/                  # Static assets
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   └── robots.txt
│   ├── src/                     # Frontend source code
│   │   ├── assets/              # Images, fonts, etc.
│   │   ├── components/          # Reusable UI components
│   │   │   ├── common/          # Generic components
│   │   │   ├── documents/       # Document-related components
│   │   │   ├── layout/          # Layout components
│   │   │   └── xml/             # XML-specific components
│   │   ├── contexts/            # React contexts
│   │   ├── hooks/               # Custom React hooks
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard/
│   │   │   ├── Documents/
│   │   │   ├── Verification/
│   │   │   └── XmlAnalysis/
│   │   ├── services/            # API client services
│   │   │   ├── api.ts           # Base API client
│   │   │   ├── documents.ts     # Document API
│   │   │   └── verification.ts  # Verification API
│   │   ├── types/               # TypeScript type definitions
│   │   ├── utils/               # Utility functions
│   │   ├── App.tsx              # Root component
│   │   ├── index.tsx            # Entry point
│   │   └── routes.tsx           # Application routes
│   ├── .eslintrc.js             # ESLint configuration
│   ├── .prettierrc              # Prettier configuration
│   ├── package.json             # Frontend dependencies
│   ├── tsconfig.json            # TypeScript configuration
│   └── vite.config.js           # Vite build configuration
├── scripts/                     # Scripts directory
│   ├── ap.sh                    # CLI script
│   ├── dev.sh                   # Development script
│   ├── xml_agent_cli.py         # XML agent CLI
│   └── xml_cli.py               # XML document CLI
├── tests/                       # Backend tests
│   └── ...
├── .env.example                 # Environment variables example
├── .gitignore                   # Git ignore file
├── docker-compose.yml           # Docker Compose for development
├── Dockerfile                   # Docker configuration
├── package.json                 # Root package.json for scripts
├── pyproject.toml               # Python project configuration
└── README.md                    # Project documentation
```

## Technology Stack

### Frontend Technologies

- **Framework**: React with TypeScript
- **Build Tool**: Vite (faster builds than webpack)
- **Styling**: Tailwind CSS with custom components
- **State Management**: React Context API + React Query for server state
- **API Client**: Axios with interceptors
- **Testing**: Jest + React Testing Library

### Backend Integration

- **API**: REST API exposed by FastAPI backend
- **Authentication**: JWT-based auth with token refresh
- **WebSockets**: For real-time updates on verification tasks
- **Documentation**: OpenAPI/Swagger for API documentation

## Key Components

### Document Viewer Components

```tsx
// XML Document Viewer
const XmlDocumentViewer: React.FC<{ docId: string }> = ({ docId }) => {
  const { data, isLoading, error } = useXmlDocument(docId);
  
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div className="xml-document-viewer">
      <XmlDocumentHeader document={data} />
      <XmlContentPanel content={data.content} />
      <XmlNodesList nodes={data.researchable_nodes} />
    </div>
  );
};
```

### Verification Components

```tsx
// Verification Plan Component
const VerificationPlan: React.FC<{ docId: string }> = ({ docId }) => {
  const { plan, isLoading, generatePlan } = useVerificationPlan(docId);
  
  return (
    <div className="verification-plan">
      <PlanHeader>
        <h2>Verification Plan</h2>
        <Button onClick={() => generatePlan()}>Generate Plan</Button>
      </PlanHeader>
      
      {isLoading ? (
        <LoadingSpinner />
      ) : (
        <>
          <PlanSummary 
            priority={plan.priority}
            nodeCount={plan.node_count}
            estimatedTime={plan.estimated_time_minutes}
          />
          <TasksList tasks={plan.tasks} />
        </>
      )}
    </div>
  );
};
```

## API Integration

The frontend will communicate with the backend through a REST API client:

```typescript
// services/api.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request/response interceptors for auth, error handling, etc.

export default api;

// services/documents.ts
import api from './api';
import { XmlDocument, DocumentList } from '../types';

export const documentsApi = {
  listDocuments: async (docType?: string): Promise<DocumentList> => {
    const response = await api.get('/documents', {
      params: { doc_type: docType },
    });
    return response.data;
  },
  
  getXmlDocument: async (docId: string): Promise<XmlDocument> => {
    const response = await api.get(`/documents/${docId}/xml`);
    return response.data;
  },
  
  uploadXmlDocument: async (content: string, title: string): Promise<XmlDocument> => {
    const response = await api.post('/xml/upload', {
      xml_content: content,
      title,
    });
    return response.data;
  },
};
```

## Custom Hooks

Custom hooks will simplify interaction with the API:

```typescript
// hooks/useXmlDocument.ts
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { documentsApi } from '../services/documents';

export function useXmlDocument(docId: string) {
  return useQuery(['xml', docId], () => documentsApi.getXmlDocument(docId));
}

export function useUploadXml() {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ content, title }: { content: string; title: string }) => 
      documentsApi.uploadXmlDocument(content, title),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('documents');
      },
    }
  );
}
```

## Authentication

Authentication will be handled using JWT tokens:

```typescript
// services/auth.ts
import api from './api';

export const authApi = {
  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    const { access_token, refresh_token } = response.data;
    
    // Store tokens in localStorage or secure cookie
    localStorage.setItem('access_token', access_token);
    localStorage.setItem('refresh_token', refresh_token);
    
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Add authentication interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Development Setup

To run both frontend and backend during development:

```bash
# Start backend
./scripts/ap.sh server

# Start frontend (in another terminal)
cd frontend
npm run dev
```

Or using the dev script:

```bash
# Start both frontend and backend
./scripts/dev.sh
```

## Docker Integration

For containerized development and deployment:

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
    environment:
      - PYTHONPATH=/app

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app/frontend
      - /app/frontend/node_modules
    depends_on:
      - backend
```

## Deployment Considerations

For production deployment:

1. **Static Frontend**: Build the frontend into static assets that can be served by Nginx or a CDN
2. **Backend API**: Deploy the FastAPI backend with gunicorn and uvicorn workers
3. **Environment Variables**: Use environment variables for configuration
4. **Authentication**: Implement proper JWT token handling with refresh
5. **CORS**: Configure CORS settings properly for production
6. **SSL**: Ensure all communication is over HTTPS

## Current Implementation

We have implemented a simple prototype frontend using:

- **FastAPI Server**: To serve HTML, JS, and handle API requests
- **Vanilla JavaScript**: For basic interactivity 
- **Tailwind CSS**: For styling (via CDN)
- **React**: Loaded via CDN for component-based structure

The prototype demonstrates:
- Basic document listing and filtering
- XML document content viewing
- Researchable nodes exploration
- Simulated research workflow

### Simple Frontend Structure

```
frontend/
├── static/              # Static assets
│   └── js/              # JavaScript files
│       ├── app.js       # Main React application
│       └── main.js      # Simpler test implementation
├── templates/           # HTML templates
│   ├── index.html       # Main application template
│   └── fallback.html    # Simple fallback page
└── server.py            # FastAPI frontend server
```

## Next Steps

### Immediate Priorities

1. Integrate the prototype with actual research workflow
2. Improve error handling and loading states
3. Add document upload functionality
4. Enhance visualization of research results

### Medium-term Goals

1. Implement the full React frontend as outlined above
2. Create core API client services
3. Implement complete document management
4. Add authentication and user management
5. Develop full XML document research features

### Design Considerations

Based on initial user feedback, we should focus on:

1. **Simplicity**: Keep the interface intuitive and focused
2. **Visualization**: Provide clear visualizations of research results
3. **Workflow Integration**: Seamlessly connect with the research workflow
4. **Performance**: Ensure responsive experience even with large XML documents
5. **Accessibility**: Build with accessibility in mind from the start