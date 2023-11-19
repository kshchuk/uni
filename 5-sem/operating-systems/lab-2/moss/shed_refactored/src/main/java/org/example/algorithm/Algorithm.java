package org.example.algorithm;

import org.example.process.Results;

import java.util.Vector;

public interface Algorithm {
    Results run(int runtime, Vector processVector, Results result);
}
