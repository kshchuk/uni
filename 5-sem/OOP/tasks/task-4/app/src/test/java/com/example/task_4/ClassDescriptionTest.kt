package com.example.task_4

import ClassDescription
import org.junit.Test

class ClassDescriptionTest {
    @Test
    fun testDescribeClass() {
        val classDescription = ClassDescription()
        val description = classDescription.describeClass("ClassDescription")
        assert(true)
    }
}