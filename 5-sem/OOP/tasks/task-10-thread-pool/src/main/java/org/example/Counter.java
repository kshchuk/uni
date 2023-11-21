package org.example;

public class Counter {
    public Double count(double a){
        for (int i = 0; i < 1000000; i++) {
            a += Math.tan(a);
        }
        return a;
    }
}
