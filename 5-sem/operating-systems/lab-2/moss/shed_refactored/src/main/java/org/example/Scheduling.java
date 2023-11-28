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
    String line;
    int cputime;
    int ioblocking;
    double alpha = 0.0;
    int standIoblockingDev = 0;
    int baseEstimatedExecutionTime = 0;
    double X;

    try {   
      //BufferedReader in = new BufferedReader(new FileReader(f));
      DataInputStream in = new DataInputStream(new FileInputStream(f));
      while ((line = in.readLine()) != null) {
        if (line.startsWith("numprocess")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          processnum = Common.parseInt(st.nextToken());
        }
        if (line.startsWith("run_time_average")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          runTimeAverage = Common.parseInt(st.nextToken());
        }
        if (line.startsWith("run_time_stddev")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          runTimeStddev = Common.parseInt(st.nextToken());
        }
        if (line.startsWith("stand_io_blocking_dev")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          standIoblockingDev = Common.parseInt(st.nextToken());
        }
        if (line.startsWith("base_estimated_execution_time")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          baseEstimatedExecutionTime = Common.parseInt(st.nextToken());
        }
        if (line.startsWith("alpha")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          alpha = Common.parseDouble(st.nextToken());
        }
        if (line.startsWith("process")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          ioblocking = Common.parseInt(st.nextToken());
          X = Common.RandomDouble();
          while (X == -1.0) {
            X = Common.RandomDouble();
          }
          X = X * runTimeStddev;
          cputime = (int) X + runTimeAverage;
          var process = new Process(cputime,ioblocking,0,0,0);
          processVector.addElement(process);
        }
        if (line.startsWith("runtime")) {
          StringTokenizer st = new StringTokenizer(line);
          st.nextToken();
          runtime = Common.parseInt(st.nextToken());
        }
      }

      for (int i = 0; i < processVector.size(); i++) {
        Process process = processVector.elementAt(i);
        process.setAlpha(alpha);
        process.setStandIoblockingDev(standIoblockingDev);
        process.estimatedExecutionTime = baseEstimatedExecutionTime;
      }

      in.close();
    } catch (IOException e) {
        System.out.println("Scheduling: error, read of " + f.getName() + " failed.");
        System.exit(-1);
    }
  }

  public static void main(String[] args) {
    int i;

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
    System.out.println("Working...");
    Init(args[0]);
    if (processVector.size() < processnum) {
      i = 0;
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
    result = SchedulingAlgorithm.Run(runtime, processVector, result);
    try {
      //BufferedWriter out = new BufferedWriter(new FileWriter(resultsFile));
      String resultsFile = "summary/Summary-Results";
      PrintStream out = new PrintStream(new FileOutputStream(resultsFile));
      out.println("Scheduling Type: " + result.schedulingType);
      out.println("Scheduling Name: " + result.schedulingName);
      out.println("Simulation Run Time: " + result.compuTime);
      out.println("Mean: " + runTimeAverage);
      out.println("Standard Deviation: " + runTimeStddev);
      out.println("Process #\tCPU Time\tIO Blocking\tCPU Completed\tCPU Blocked");
      for (i = 0; i < processVector.size(); i++) {
        Process process = processVector.elementAt(i);
        out.print(i + "    ");
        if (i < 100) { out.print("\t\t"); } else { out.print("\t"); }
        out.print(process.cputime);
        if (process.cputime < 100) { out.print(" (ms)\t\t"); } else { out.print(" (ms)\t"); }
        out.print(process.ioblocking);
        if (process.ioblocking < 100) { out.print(" (ms)\t\t"); } else { out.print(" (ms)\t"); }
        out.print(process.cpudone);
        if (process.cpudone < 100) { out.print(" (ms)\t\t"); } else { out.print(" (ms)\t"); }
        out.println(process.numblocked + " times");
      }
      out.close();
    } catch (IOException e) {
        System.out.println("Scheduling: error, write of results failed.");
        System.exit(-1);
    }
  System.out.println("Completed.");
  }
}

