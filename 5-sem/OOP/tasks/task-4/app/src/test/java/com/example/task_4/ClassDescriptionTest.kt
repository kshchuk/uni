package com.example.task_4

import ClassDescription
import org.junit.Test
import android.util.Log

inline fun <reified T> T.logi(message: String) = Log.i(T::class.java.simpleName, message)

class ClassDescriptionTest {
    @Test
    fun testDescribeClass() {
        val classDescription = ClassDescription()
        val description = classDescription.describeClass("ClassDescriptionTest")
        logi(description)
    }
}