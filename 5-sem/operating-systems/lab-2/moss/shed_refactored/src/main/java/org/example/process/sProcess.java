package org.example.process;

import org.example.common.Common;

public class sProcess {
  public int cputime;
  public int ioblocking;
  public int cpudone;
  public int ionext;
  public int numblocked;
  public int standIoblockingDev;
  public boolean isBlocked = false;
  public int timeToUnblock = 0;

  // aging variables
  public double alpha;
  public double estimatedExecutionTime;

  public sProcess(int cputime, int ioblocking, int cpudone, int ionext, int numblocked) {
    this.cputime = cputime;
    this.ioblocking = ioblocking;
    this.cpudone = cpudone;
    this.ionext = ionext;
    this.numblocked = numblocked;
  }

  public void setAlpha(double alpha) {
    this.alpha = alpha;
  }

  public void setStandIoblockingDev(int standIoblockingDev) {
    this.standIoblockingDev = standIoblockingDev;
  }

  public void calculateEstimateExecutionTime() {
    if (estimatedExecutionTime == 0) {
      estimatedExecutionTime = ioblocking;
    }
    else {
      estimatedExecutionTime = alpha * ioblocking + (1 - alpha) * estimatedExecutionTime;
    }
  }

  public void tryUnblock() {
    timeToUnblock--;
    if (timeToUnblock == 0) {
      isBlocked = false;
    }
  }

  public void calculateIoBlocking() {
    double X = Common.RandomDouble();
    while (X == -1.0) {
      X = Common.RandomDouble();
    }
    X = X * standIoblockingDev;
    this.ioblocking = (int) X + ioblocking;
  }

  public void block() {
    isBlocked = true;
    timeToUnblock = ioblocking;
    numblocked++;
    ionext = 0;
  }
}
