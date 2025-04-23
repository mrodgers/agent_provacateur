declare module 'node-nlp' {
  export class NlpManager {
    constructor(options?: any);
    train(): Promise<void>;
    isRunning(): boolean;
    process(locale: string, text: string): Promise<any>;
  }
}