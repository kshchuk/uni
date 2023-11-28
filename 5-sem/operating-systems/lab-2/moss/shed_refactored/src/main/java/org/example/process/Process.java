package org.example.process;

import org.example.common.Common;

// This class represents a process in the scheduling simulation.
public class Process {
  // The total CPU time required by the process.
  public int cputime;
  // The time the process will block for I/O.
  public int ioblocking;
  // The amount of CPU time the process has received so far.
  public int cpudone;
  // The time at which the process will next block for I/O.
  public int ionext;
  // The number of times the process has been blocked.
  public int numblocked;
  // The standard deviation of the I/O blocking time.
  public int standIoblockingDev;
  // A flag indicating whether the process is currently blocked.
  public boolean isBlocked = false;
  // The time remaining until the process becomes unblocked.
  public int timeToUnblock;

  // aging variables
  // The alpha value used in the aging calculation.
  public double alpha;
  // The estimated remaining execution time of the process.
  public double estimatedExecutionTime;

  // Constructor for the Process class.
  public Process(int cputime, int ioblocking, int cpudone, int ionext, int numblocked) {
    this.cputime = cputime;
    this.ioblocking = ioblocking;
    this.cpudone = cpudone;
    this.ionext = ionext;
    this.numblocked = numblocked;
  }

  // Setter for the alpha value.
  public void setAlpha(double alpha) {
    this.alpha = alpha;
  }

  // Setter for the standard deviation of the I/O blocking time.
  public void setStandIoblockingDev(int standIoblockingDev) {
    this.standIoblockingDev = standIoblockingDev;
  }

  // Method to calculate the estimated remaining execution time.
  public void calculateEstimateExecutionTime() {
    if (estimatedExecutionTime == 0) {
      estimatedExecutionTime = ioblocking;
    }
    else {
      estimatedExecutionTime = alpha * ioblocking + (1 - alpha) * estimatedExecutionTime;
    }
  }

  // Method to attempt to unblock the process.
  public void tryUnblock() {
    timeToUnblock--;
    if (timeToUnblock == 0) {
      isBlocked = false;
    }
  }

  // Method to calculate the I/O blocking time.
  public void calculateIoBlocking() {
    double X = Common.RandomDouble();
    while (X == -1.0) {
      X = Common.RandomDouble();
    }
    X = X * standIoblockingDev;
    this.ioblocking = (int) X + ioblocking;
  }

  // Method to block the process.
  public void block() {
    isBlocked = true;
    timeToUnblock = ioblocking;
    numblocked++;
    ionext = 0;
  }
}
