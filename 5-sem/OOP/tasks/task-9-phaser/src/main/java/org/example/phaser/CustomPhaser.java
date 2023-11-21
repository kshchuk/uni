package org.example.phaser;

import java.util.logging.Level;
import java.util.logging.Logger;

public class CustomPhaser {
    private static final Logger log = Logger.getLogger(CustomPhaser.class.getName());
    private int parties;
    private Integer partiesAwait = 0;
    private int phase;

    public CustomPhaser(int parties) {
        this.parties = parties;
        this.partiesAwait = parties;
    }

    int register(){
        parties++;
        partiesAwait++;
        return phase;
    }

    int arrive(){
        partiesAwait--;
        int currentPhase = phase;
        synchronized (this){
            if(partiesAwait == 0){
                notifyAll();
                partiesAwait = parties;
                phase = currentPhase + 1;
            }
        }
        return phase;
    }

    int arriveAndAwaitAdvance(){
        partiesAwait--;
        int currentPhase = phase;
        synchronized (this){
            while (partiesAwait > 0){
                try {
                    this.wait();
                } catch (InterruptedException e) {
                    log.log(Level.SEVERE, "Exception: ", e);
                }
            }
        }
        partiesAwait = parties;
        phase = currentPhase + 1;
        synchronized (this){
            notifyAll();
        }
        return phase;
    }

    int arriveAndDeregister(){
        --partiesAwait;
        --parties;
        int currentPhase = phase;
        synchronized (this){
            if(partiesAwait == 0){
                notifyAll();
                phase = currentPhase + 1;
                partiesAwait = parties;
                return -1;
            }
        }
        return phase + 1;
    }

    public int getPhase() {
        return phase;
    }
}
