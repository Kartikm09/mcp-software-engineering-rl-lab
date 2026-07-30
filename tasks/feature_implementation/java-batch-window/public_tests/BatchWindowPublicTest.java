public final class BatchWindowPublicTest {
    public static void main(String[] args) {
        BatchWindow window = new BatchWindow(10);
        if (window.remainingCapacity(4) != 6) {
            throw new AssertionError("remaining capacity should be 6");
        }
        if (!window.canAccept(4, 5)) {
            throw new AssertionError("request below capacity should be accepted");
        }
    }
}

