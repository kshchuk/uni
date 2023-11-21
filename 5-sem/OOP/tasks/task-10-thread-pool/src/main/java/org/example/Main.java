package org.example;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;
import org.example.pool.ThreadPool;

import static java.lang.String.format;

public class Main {
    public static void main(String[] args) throws ExecutionException, InterruptedException {
        // ExecutorService threadPool = Executors.newFixedThreadPool(9);
        ThreadPool threadPool = new ThreadPool(2);
        Counter counter = new Counter();

        long start = System.nanoTime();

        List<Future<Double>> futures = new ArrayList<>();
        for (int i = 0; i < 400; i++) {
            final int j = i;
            futures.add(
                    CompletableFuture.supplyAsync(
                            ()-> counter.count(j), threadPool
                    ));
        }
        double sumOfFutures = 0;
        for (Future<Double> future: futures){
            sumOfFutures += future.get();
        }
        System.out.println(format("Executed by %d s, value: %f",
                (System.nanoTime() - start)/1000_000_000, sumOfFutures));

        threadPool.shutdown();
    }
}