package org.example.algorithm;

import org.example.process.Results;
import org.example.process.Process;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.util.Vector;

public class FirstComeFirstServed implements Algorithm{
    @Override
    public Results run(int runtime, Vector processVector, Results result){
        int i;
        int comptime = 0;
        int currentProcess = 0;
        int previousProcess;
        int size = processVector.size();
        int completed = 0;
        String resultsFile = "summary/Summary-Processes";

        result.schedulingType = "Batch (Nonpreemptive)";
        result.schedulingName = "First-Come First-Served";
        try {
            PrintStream out = new PrintStream(new FileOutputStream(resultsFile));
            Process process = (Process) processVector.elementAt(currentProcess);
            out.println("Process: " + currentProcess + " registered... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.cpudone + ")");
            while (comptime < runtime) {
                if (process.cpudone == process.cputime) {
                    completed++;
                    out.println("Process: " + currentProcess + " completed... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.cpudone + ")");
                    if (completed == size) {
                        result.compuTime = comptime;
                        out.close();
                        return result;
                    }
                    for (i = size - 1; i >= 0; i--) {
                        process = (Process) processVector.elementAt(i);
                        if (process.cpudone < process.cputime) {
                            currentProcess = i;
                        }
                    }
                    process = (Process) processVector.elementAt(currentProcess);
                    out.println("Process: " + currentProcess + " registered... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.cpudone + ")");
                }
                if (process.ioblocking == process.ionext) {
                    out.println("Process: " + currentProcess + " I/O blocked... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.cpudone + ")");
                    process.numblocked++;
                    process.ionext = 0;
                    previousProcess = currentProcess;
                    for (i = size - 1; i >= 0; i--) {
                        process = (Process) processVector.elementAt(i);
                        if (process.cpudone < process.cputime && previousProcess != i) {
                            currentProcess = i;
                        }
                    }
                    process = (Process) processVector.elementAt(currentProcess);
                    out.println("Process: " + currentProcess + " registered... (" + process.cputime + " " + process.ioblocking + " " + process.cpudone + " " + process.cpudone + ")");
                }
                process.cpudone++;
                if (process.ioblocking > 0) {
                    process.ionext++;
                }
                comptime++;
            }
            out.close();
        } catch (IOException e) {
            System.out.println("Scheduling: error, read of " + resultsFile + " failed.");
            System.exit(-1);
        }
        result.compuTime = comptime;
        return result;
    }
}
