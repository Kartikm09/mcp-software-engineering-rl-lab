export class IdempotencyGate<T> {
  private readonly completed = new Map<string, T>();

  async run(key: string, operation: () => Promise<T>): Promise<T> {
    const completed = this.completed.get(key);
    if (completed !== undefined) {
      return completed;
    }

    const value = await operation();
    this.completed.set(key, value);
    return value;
  }
}

