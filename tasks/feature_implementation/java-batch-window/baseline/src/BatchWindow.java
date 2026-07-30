public final class BatchWindow {
    private final int maxSize;

    public BatchWindow(int maxSize) {
        if (maxSize < 1) {
            throw new IllegalArgumentException("maxSize must be positive");
        }
        this.maxSize = maxSize;
    }

    public boolean canAccept(int currentSize, int requested) {
        return currentSize >= 0 && requested > 0 && currentSize + requested < maxSize;
    }
}

