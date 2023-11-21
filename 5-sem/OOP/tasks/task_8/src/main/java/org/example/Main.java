package org.example;

import org.example.lock.CustomLock;
import org.example.lock.CustomReentrantLock;

import java.util.logging.Level;
import java.util.logging.Logger;

public class Main {
    public static void main(String[] args) {
        CustomLock lockCustom = new CustomReentrantLock();
        MyRunnable myRunnable = new MyRunnable(lockCustom);
        new Thread(myRunnable,"Thread-1").start();
        new Thread(myRunnable,"Thread-2").start();
    }
}


class MyRunnable implements Runnable{
    private static final Logger log = Logger.getLogger(MyRunnable.class.getName());

    private final CustomLock lockCustom;

    public MyRunnable(CustomLock lockCustom) {
        this.lockCustom=lockCustom;
    }

    public void run(){
        log.info(Thread.currentThread().getName() +" is waiting to acquire CustomReentrantLock");
        lockCustom.lock();
        log.info(Thread.currentThread().getName() +" has acquired CustomReentrantLock.");
        try {
            Thread.sleep(3000);
            log.info(Thread.currentThread().getName() +" is sleeping.");
        } catch (InterruptedException e) {
            log.log(Level.SEVERE, "Exception: ", e);
        }
        log.info(Thread.currentThread().getName() +" has released CustomReentrantLock.");
        lockCustom.unlock();
    }
}