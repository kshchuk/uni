package org.example.phaser;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class CustomPhaserTest {
    private CustomPhaser customPhaser;
    int currentPhase = 0;

    @BeforeEach
    public void setUp(){
        customPhaser = new CustomPhaser(3);
    }

    void createThread() {
        Thread thread = new Thread(() -> {
            currentPhase = customPhaser.arrive();
        });
        thread.start();
    }

    void createThreadWithAwait() {
        Thread thread = new Thread(() -> {
            currentPhase = customPhaser.arriveAndAwaitAdvance();
        });
        thread.start();
    }

    void createThreadWithDeregister() {
        Thread thread = new Thread(() -> {
            currentPhase = customPhaser.arriveAndDeregister();
        });
        thread.start();
    }

    @Test
    void shouldReachThirdPhase() throws InterruptedException {
        createThreadWithAwait();
        createThreadWithAwait();
        createThreadWithAwait();
        synchronized (this) {
            this.wait(2500);
        }
        createThreadWithAwait();
        createThreadWithAwait();
        createThreadWithAwait();
        synchronized (this) {
            this.wait(2500);
        }
        assertEquals(2, currentPhase);
    }

    @Test
    void shouldReachSecondPhaseWithAwait() throws InterruptedException {
        createThread();
        createThreadWithAwait();
        createThread();
        synchronized (this) {
            this.wait(2500);
        }
        assertEquals(1, currentPhase);
    }

    @Test
    void shouldReachSecondPhase() throws InterruptedException {
        createThread();
        createThread();
        createThread();
        synchronized (this) {
            this.wait(2500);
        }
        assertEquals(1, currentPhase);
    }

    @Test
    void shouldReachThirdPhaseWithDeregister() throws InterruptedException {
        customPhaser.arrive();
        createThreadWithDeregister();
        createThreadWithDeregister();
        synchronized (this) {
            this.wait(2500);
        }
        currentPhase = customPhaser.arrive();
        assertEquals(2, currentPhase);
    }
}
