package org.example.algorithm;

import org.example.process.Results;
import org.example.process.sProcess;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.util.Vector;

public class ShortestProcessNext implements Algorithm {
    @Override
    public Results run(int runtime, Vector processVector, Results result){
        int i = 0;
        int comptime = 0;
        int currentProcess = 0;
        int size = processVector.size();
        int completed = 0;
        String resultsFile = "summary/Summary-Processes";

        result.schedulingType = "Interactive (Nonpreemptive)";
        result.schedulingName = "Shortest Process Next";
        try {
            PrintStream out = new PrintStream(new FileOutputStream(resultsFile));
            sProcess process = getShortestProcess(processVector);
            currentProcess = processVector.indexOf(process);
            out.println("Process: " + currentProcess + " registered... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.estimatedExecutionTime + ")");
            while (comptime < runtime) {
                if (process.cpudone == process.cputime) {
                    completed++;
                    out.println("Process: " + currentProcess + " completed... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.estimatedExecutionTime + ")");
                    if (completed == size) {
                        result.compuTime = comptime;
                        out.close();
                        return result;
                    }
                    process = getShortestProcess(processVector);
                    currentProcess = processVector.indexOf(process);
                    out.println("Process: " + currentProcess + " registered... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.estimatedExecutionTime + ")");
                }

                if (process.ioblocking == process.ionext) {
                    process.numblocked++;
                    process.ionext = 0;
                    out.println("Process: " + currentProcess + " I/O blocked... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.estimatedExecutionTime + ")");
                    process.calculateEstimateExecutionTime();
                    process.calculateIoBlocking();

                    process = (sProcess) processVector.elementAt(currentProcess);
                    out.println("Process: " + currentProcess + " registered... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.estimatedExecutionTime + ")");
                }

                process.cpudone++;
                if (process.ioblocking > 0) {
                    process.ionext++;
                }
                comptime++;
            }
            out.close();
        } catch (IOException e) { /* Handle exceptions */ }
        result.compuTime = comptime;
        return result;
    }

    private sProcess getShortestProcess(Vector processVector) {
        sProcess shortestProcess = (sProcess) processVector.elementAt(0);
        for (int i = 1; i < processVector.size(); i++) {
            sProcess process = (sProcess) processVector.elementAt(i);
            if (process.cpudone < process.cputime && process.estimatedExecutionTime < shortestProcess.estimatedExecutionTime) {
                shortestProcess = process;
            }
        }
        return shortestProcess;
    }
}