package org.example.algorithm;

import org.example.process.Results;
import org.example.process.Process;

import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintStream;
import java.util.Vector;

public class ShortestProcessNext implements Algorithm {
    @Override
    public Results run(int runtime, Vector processVector, Results result){
        int comptime = 0;
        int currentProcess;
        int size = processVector.size();
        int completed = 0;
        String resultsFile = "summary/Summary-Processes";

        result.schedulingType = "Interactive (Nonpreemptive)";
        result.schedulingName = "Shortest Process Next";
        try {
            PrintStream out = new PrintStream(new FileOutputStream(resultsFile));
            out.println("Current process              CPU time   IO blocking   CPU done   Estimated execution time");
            Process process = getShortestProcess(processVector);

            if (process == null) {
                result.compuTime = comptime;
                out.close();
                return result;
            }

            currentProcess = processVector.indexOf(process);
            printProcessRegistered(out, process, currentProcess);
            while (comptime < runtime) {
                if (process.cpudone == process.cputime) {
                    completed++;
                    printProcessCompleted(out, process, currentProcess);
                    if (completed == size) {
                        result.compuTime = comptime;
                        out.close();
                        return result;
                    }
                    process = getShortestProcess(processVector);

                    if (process == null) {
                        while (process == null && comptime < runtime) {
                            comptime++;
                            this.idleTime(processVector);
                            process = getShortestProcess(processVector);
                        }
                        continue;
                    }

                    currentProcess = processVector.indexOf(process);
                    printProcessRegistered(out, process, currentProcess);
                }

                if (process.ioblocking == process.ionext) {
                    process.block();
                    process.calculateEstimateExecutionTime();
                    printProcessBlocked(out, process, currentProcess);
                    process.calculateIoBlocking();

                    process = getShortestProcess(processVector);

                    if (process == null) {
                        while (process == null && comptime < runtime) {
                            comptime++;
                            this.idleTime(processVector);
                            process = getShortestProcess(processVector);
                        }
                        continue;
                    }

                    currentProcess = processVector.indexOf(process);
                    printProcessRegistered(out, process, currentProcess);
                }

                process.cpudone++;
                if (process.ioblocking > 0) {
                    process.ionext++;
                }
                comptime++;
                this.idleTime(processVector);
            }
            out.close();
        } catch (IOException e) {
            System.out.println("Scheduling: error, read of " + resultsFile + " failed.");
            System.exit(-1);
        }
        result.compuTime = comptime;
        return result;
    }

    private Process getShortestProcess(Vector<Process> processVector) {

        Process shortestProcess;
        do {
            shortestProcess = null;
            for (int i = 0; i < processVector.size(); i++) {
                Process process = processVector.elementAt(i);
                if (process.isBlocked || process.cpudone == process.cputime) {
                    continue;
                }
                if (shortestProcess == null || process.cputime < shortestProcess.cputime) {
                    shortestProcess = process;
                }
            }
            if (shortestProcess == null) {
                return null;
            }
        } while (shortestProcess.isBlocked);

        if (processVector.indexOf(shortestProcess) == 0 && shortestProcess.isBlocked) {
            var newVector = new Vector<>(processVector);
            newVector.removeElementAt(0);
            return this.getShortestProcess(newVector);
        }

        if (shortestProcess.isBlocked || shortestProcess.cpudone == shortestProcess.cputime) {
            return null;
        }

        return shortestProcess;
    }

    private void idleTime(Vector<Process> processVector) {
        for (int i = 0; i < processVector.size(); i++) {
            Process process = processVector.elementAt(i);
            if (process.isBlocked) {
                process.tryUnblock();
            }
        }
    }

    private void printProcessRegistered(PrintStream out, Process process, int currentProcess) {
        out.println("Process: " + currentProcess + "  registered... (          " + process.cputime + "          " + process.ioblocking + "           " + process.cpudone + "         " + process.estimatedExecutionTime + ")");
    }

    private void printProcessBlocked(PrintStream out, Process process, int currentProcess) {
        out.println("Process: " + currentProcess + " I/O blocked... (          " + process.cputime + "          " + process.ioblocking + "           " + process.cpudone + "         " + process.estimatedExecutionTime + ")");
    }

    private void printProcessCompleted(PrintStream out, Process process, int currentProcess) {
        out.println("Process: " + currentProcess + "   completed... (          " + process.cputime + "          " + process.ioblocking + "           " + process.cpudone + "         " + process.estimatedExecutionTime + ")");
    }
}