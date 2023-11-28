package org.example;

// This file contains the main() function for the Scheduling
// simulation.  Init() initializes most of the variables by
// reading from a provided file.  SchedulingAlgorithm.Run() is
// called from main() to run the simulation.  Summary-Results
// is where the summary results are written, and Summary-Processes
// is where the process scheduling summary is written.

// Created by Alexander Reeder, 2001 January 06
// Modified by Yaroslav Kishchuk, 2023 November 19


import org.example.process.Results;
import org.example.algorithm.SchedulingAlgorithm;
import org.example.common.Common;
import org.example.process.Process;

import java.io.*;
import java.util.StringTokenizer;
import java.util.Vector;

public class Scheduling {
  private static int processnum = 5;
  private static int runTimeAverage = 1000;
  private static int runTimeStddev = 100;
  private static int runtime = 1000;
  private static final Vector<Process> processVector = new Vector<>();
  private static Results result = new Results("null","null",0);

  private static void Init(String file) {
    File f = new File(file);
    int cputime;
    int ioblocking;
    double alpha = 0.0;
    int standIoblockingDev = 0;
    int baseEstimatedExecutionTime = 0;
    double X;

    try (BufferedReader in = new BufferedReader(new FileReader(f))) {
      String line;
      while ((line = in.readLine()) != null) {
        if (line.isEmpty()) {
          continue;
        }
        StringTokenizer st = new StringTokenizer(line);
        String token = st.nextToken();
        switch (token) {
          case "numprocess":
            processnum = Common.parseInt(st.nextToken());
            break;
          case "run_time_average":
            runTimeAverage = Common.parseInt(st.nextToken());
            break;
          case "run_time_stddev":
            runTimeStddev = Common.parseInt(st.nextToken());
            break;
          case "stand_io_blocking_dev":
            standIoblockingDev = Common.parseInt(st.nextToken());
            break;
          case "base_estimated_execution_time":
            baseEstimatedExecutionTime = Common.parseInt(st.nextToken());
            break;
          case "alpha":
            alpha = Common.parseDouble(st.nextToken());
            break;
          case "process":
            ioblocking = Common.parseInt(st.nextToken());
            X = Common.RandomDouble();
            while (X == -1.0) {
              X = Common.RandomDouble();
            }
            X = X * runTimeStddev;
            cputime = (int) X + runTimeAverage;
            var process = new Process(cputime,ioblocking,0,0,0);
            processVector.addElement(process);
            break;
          case "runtime":
            runtime = Common.parseInt(st.nextToken());
            break;
        }
      }

      for (Process process : processVector) {
        process.setAlpha(alpha);
        process.setStandIoblockingDev(standIoblockingDev);
        process.estimatedExecutionTime = baseEstimatedExecutionTime;
      }
    } catch (IOException e) {
      System.out.println("Scheduling: error, read of " + f.getName() + " failed.");
      System.exit(-1);
    }
  }

  public static void main(String[] args) {
    validateInput(args);
    System.out.println("Working...");
    Init(args[0]);
    fillProcessVector();
    result = SchedulingAlgorithm.run(runtime, processVector, result);
    writeResults();
    System.out.println("Completed.");
  }

  private static void validateInput(String[] args) {
    if (args.length != 1) {
      System.out.println("Usage: 'java Scheduling <INIT FILE>'");
      System.exit(-1);
    }
    File f = new File(args[0]);
    if (!(f.exists())) {
      System.out.println("Scheduling: error, file '" + f.getName() + "' does not exist.");
      System.exit(-1);
    }
    if (!(f.canRead())) {
      System.out.println("Scheduling: error, read of " + f.getName() + " failed.");
      System.exit(-1);
    }
  }

  private static void fillProcessVector() {
    if (processVector.size() < processnum) {
      int i = 0;
      while (processVector.size() < processnum) {
        double X = Common.RandomDouble();
        while (X == -1.0) {
          X = Common.RandomDouble();
        }
        X = X * runTimeStddev;
        int cputime = (int) X + runTimeAverage;
        processVector.addElement(new Process(cputime,i*100,0,0,0));
        i++;
      }
    }
  }

  private static void writeResults() {
    try {
      String resultsFile = "summary/Summary-Results";
      try (PrintStream out = new PrintStream(new FileOutputStream(resultsFile))) {
        out.println("Scheduling Type: " + result.schedulingType);
        out.println("Scheduling Name: " + result.schedulingName);
        out.println("Simulation Run Time: " + result.compuTime);
        out.println("Mean: " + runTimeAverage);
        out.println("Standard Deviation: " + runTimeStddev);
        out.println("Process #\tCPU Time\tIO Blocking\tCPU Completed\tCPU Blocked");
        for (int i = 0; i < processVector.size(); i++) {
          Process process = processVector.elementAt(i);
          out.printf("%d\t\t%d (ms)\t\t%d (ms)\t\t%d (ms)\t\t%d times%n", i, process.cputime, process.ioblocking, process.cpudone, process.numblocked);
        }
      }
    } catch (IOException e) {
      System.out.println("Scheduling: error, write of results failed.");
      System.exit(-1);
    }
  }
}

