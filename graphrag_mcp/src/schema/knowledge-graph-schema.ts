/**
 * Knowledge Graph Schema Manager
 * Manages the schema for the knowledge graph, including entity types and relationship types.
 */

import * as fs from 'fs';
import * as path from 'path';

interface SchemaConfig {
  path: string;
  defaultRelationships: string[];
}

interface SchemaDefinition {
  entityTypes: {
    [key: string]: EntityTypeDefinition;
  };
  relationshipTypes: {
    [key: string]: RelationshipTypeDefinition;
  };
  version: string;
  updated_at: string;
}

interface EntityTypeDefinition {
  name: string;
  description: string;
  properties: {
    [key: string]: {
      type: string;
      description: string;
      required?: boolean;
    };
  };
}

interface RelationshipTypeDefinition {
  name: string;
  description: string;
  source_types: string[];
  target_types: string[];
  properties: {
    [key: string]: {
      type: string;
      description: string;
      required?: boolean;
    };
  };
}

export class KnowledgeGraphSchema {
  private config: SchemaConfig;
  private schema: SchemaDefinition;
  
  /**
   * Initialize the knowledge graph schema manager
   * @param config Schema configuration
   */
  constructor(config: SchemaConfig) {
    this.config = config;
    this.schema = this.loadSchema();
  }
  
  /**
   * Load the schema from the schema file
   * @returns Schema definition
   */
  private loadSchema(): SchemaDefinition {
    try {
      // Check if schema file exists
      if (fs.existsSync(this.config.path)) {
        // Load schema from file
        const schemaContent = fs.readFileSync(this.config.path, 'utf-8');
        return JSON.parse(schemaContent);
      } else {
        // Create default schema
        const defaultSchema = this.createDefaultSchema();
        
        // Ensure directory exists
        const schemaDir = path.dirname(this.config.path);
        if (!fs.existsSync(schemaDir)) {
          fs.mkdirSync(schemaDir, { recursive: true });
        }
        
        // Write default schema to file
        fs.writeFileSync(this.config.path, JSON.stringify(defaultSchema, null, 2));
        
        return defaultSchema;
      }
    } catch (error: any) {
      console.error(`Error loading schema: ${error.message}`);
      
      // Return a basic default schema in case of error
      return this.createDefaultSchema();
    }
  }
  
  /**
   * Create a default schema
   * @returns Default schema definition
   */
  private createDefaultSchema(): SchemaDefinition {
    const defaultEntityTypes = {
      'person': {
        name: 'Person',
        description: 'An individual person',
        properties: {
          'name': {
            type: 'string',
            description: 'Full name of the person',
            required: true
          },
          'birth_date': {
            type: 'date',
            description: 'Birth date of the person'
          }
        }
      },
      'organization': {
        name: 'Organization',
        description: 'A company, institution, or other organization',
        properties: {
          'name': {
            type: 'string',
            description: 'Name of the organization',
            required: true
          },
          'founded': {
            type: 'date',
            description: 'Founding date of the organization'
          }
        }
      },
      'concept': {
        name: 'Concept',
        description: 'An abstract concept or idea',
        properties: {
          'name': {
            type: 'string',
            description: 'Name of the concept',
            required: true
          },
          'category': {
            type: 'string',
            description: 'Category of the concept'
          }
        }
      },
      'location': {
        name: 'Location',
        description: 'A physical location or place',
        properties: {
          'name': {
            type: 'string',
            description: 'Name of the location',
            required: true
          },
          'coordinates': {
            type: 'object',
            description: 'Geographic coordinates'
          }
        }
      },
      'event': {
        name: 'Event',
        description: 'A specific event or occurrence',
        properties: {
          'name': {
            type: 'string',
            description: 'Name of the event',
            required: true
          },
          'date': {
            type: 'date',
            description: 'Date of the event'
          }
        }
      }
    };
    
    // Use default relationships from config or fallback
    const defaultRelationships = this.config.defaultRelationships || [
      'related_to', 'part_of', 'has_part', 'is_a', 'has_property'
    ];
    
    // Build relationship type definitions
    const defaultRelationshipTypes: { [key: string]: RelationshipTypeDefinition } = {};
    
    // Create relationship types with descriptions
    const relationshipDescriptions: { [key: string]: string } = {
      'related_to': 'A general relationship between two entities',
      'part_of': 'Indicates that one entity is a part of another',
      'has_part': 'Indicates that one entity has another as a part',
      'is_a': 'Indicates that one entity is a type or instance of another',
      'has_property': 'Indicates that one entity has a property represented by another entity',
      'created_by': 'Indicates that an entity was created by another entity',
      'located_in': 'Indicates that an entity is located within another entity',
      'happened_at': 'Indicates that an event happened at a location',
      'participated_in': 'Indicates that an entity participated in an event',
      'affiliated_with': 'Indicates that an entity is affiliated with another'
    };
    
    // Add all default relationships to the schema
    defaultRelationships.forEach(relType => {
      defaultRelationshipTypes[relType] = {
        name: relType,
        description: relationshipDescriptions[relType] || `Relationship of type ${relType}`,
        source_types: Object.keys(defaultEntityTypes),
        target_types: Object.keys(defaultEntityTypes),
        properties: {
          'confidence': {
            type: 'number',
            description: 'Confidence score for this relationship (0.0-1.0)'
          },
          'source': {
            type: 'string',
            description: 'Source of this relationship information'
          }
        }
      };
    });
    
    return {
      entityTypes: defaultEntityTypes,
      relationshipTypes: defaultRelationshipTypes,
      version: '0.1.0',
      updated_at: new Date().toISOString()
    };
  }
  
  /**
   * Get all entity types defined in the schema
   * @returns List of entity type names
   */
  getEntityTypes(): string[] {
    return Object.keys(this.schema.entityTypes);
  }
  
  /**
   * Get all relationship types defined in the schema
   * @returns List of relationship type names
   */
  getRelationshipTypes(): string[] {
    return Object.keys(this.schema.relationshipTypes);
  }
  
  /**
   * Get the full schema definition
   * @returns Schema definition
   */
  getSchema(): SchemaDefinition {
    return this.schema;
  }
  
  /**
   * Update the schema (partial updates)
   * @param updates Schema updates to apply
   * @returns Updated schema
   */
  updateSchema(updates: Partial<SchemaDefinition>): SchemaDefinition {
    // Apply updates to the schema
    if (updates.entityTypes) {
      this.schema.entityTypes = {
        ...this.schema.entityTypes,
        ...updates.entityTypes
      };
    }
    
    if (updates.relationshipTypes) {
      this.schema.relationshipTypes = {
        ...this.schema.relationshipTypes,
        ...updates.relationshipTypes
      };
    }
    
    // Update version and timestamp
    this.schema.version = updates.version || 
      this.incrementVersion(this.schema.version);
    this.schema.updated_at = new Date().toISOString();
    
    // Save updated schema to file
    try {
      fs.writeFileSync(this.config.path, JSON.stringify(this.schema, null, 2));
      console.error(`Updated schema saved to ${this.config.path}`);
    } catch (error: any) {
      console.error(`Error saving schema: ${error.message}`);
    }
    
    return this.schema;
  }
  
  /**
   * Increment the version number
   * @param version Current version string (x.y.z)
   * @returns Incremented version string
   */
  private incrementVersion(version: string): string {
    const parts = version.split('.');
    if (parts.length !== 3) {
      return '0.1.0';
    }
    
    // Increment the patch version
    const patch = parseInt(parts[2], 10) + 1;
    return `${parts[0]}.${parts[1]}.${patch}`;
  }
}