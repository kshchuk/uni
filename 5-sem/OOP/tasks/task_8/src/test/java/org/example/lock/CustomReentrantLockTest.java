package org.example.lock;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class CustomReentrantLockTest {
    private CustomReentrantLock customReentrantLock;

    @BeforeEach
    public void init(){
        customReentrantLock = new CustomReentrantLock();
    }

    @Test
    public void shouldLockAndRelease() throws InterruptedException {
        Thread thread = new Thread(() -> {
            customReentrantLock.lock();
            customReentrantLock.lock();
            customReentrantLock.unlock();
            customReentrantLock.unlock();
        });
        thread.start();
        thread.join();
        assertTrue(customReentrantLock.tryLock());
        customReentrantLock.unlock();
    }

    @Test
    public void shouldReturnFalseBecauseTwoLocksOneUnlock(){
        customReentrantLock.lock();
        customReentrantLock.lock();
        customReentrantLock.unlock();
        assertFalse(customReentrantLock.tryLock());
    }
}
