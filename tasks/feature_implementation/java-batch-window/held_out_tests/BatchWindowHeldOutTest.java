public final class BatchWindowHeldOutTest {
    public static void main(String[] args) {
        BatchWindow window = new BatchWindow(10);
        if (!window.canAccept(4, 6)) {
            throw new AssertionError("request that exactly fills the batch should be accepted");
        }
        if (window.remainingCapacity(10) != 0) {
            throw new AssertionError("a full batch has no remaining capacity");
        }
        try {
            window.remainingCapacity(11);
            throw new AssertionError("oversized current state must be rejected");
        } catch (IllegalArgumentException expected) {
            // Expected.
        }
    }
}

