import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test

class ClassDescriptionTest {
    @Test
    fun testDescribeClass() {
        val classDescription = ClassDescription()
        val description = classDescription.describeClass("example.Dog")

        println(description)

        assertTrue(description.contains("Class Name: Dog"))
        assertTrue(description.contains("Package: example"))
        assertTrue(description.contains("Properties:"))
        assertTrue(description.contains("breed:"))
        assertTrue(description.contains("name:"))
        assertTrue(description.contains("Fields:"))
        assertTrue(description.contains("Methods:"))
        assertTrue(description.contains("bark"))
        assertTrue(description.contains("sleep"))
        assertTrue(description.contains("eat"))
        assertTrue(description.contains("Inheritance Hierarchy:"))
        assertTrue(description.contains("Animal"))
        assertTrue(description.contains("Interfaces:"))
        assertTrue(description.contains("Mammal"))
    }
}
