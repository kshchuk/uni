import kotlin.reflect.full.*

/**
 * A utility class for describing the structure of a Java class using reflection.
 */
class ClassDescription {
    /**
     * Get a complete description of a class with the given name, including information about
     * properties, fields, and methods.
     *
     * @param className The fully qualified class name to be described.
     * @return A string containing the class description.
     */
    fun describeClass(className: String): String {
        try {
            val clazz = Class.forName(className)
            val classInfo = StringBuilder()

            classInfo.append("Class Name: ${clazz.simpleName}\n")
            classInfo.append("Package: ${clazz.`package`?.name}\n")

            val properties = clazz.kotlin.declaredMemberProperties
            val fields = clazz.declaredFields
            val functions = clazz.kotlin.declaredMemberFunctions

            classInfo.append("\nProperties:\n")
            for (property in properties) {
                classInfo.append("${property.name}: ${property.returnType}\n")
            }

            classInfo.append("\nFields:\n")
            for (field in fields) {
                classInfo.append("${field.name}: ${field.type}\n")
            }

            classInfo.append("\nMethods:\n")
            for (function in functions) {
                classInfo.append("${function.name}(${function.parameters.joinToString { "${it.name}: ${it.type}" }}): ${function.returnType}\n")
            }

            return classInfo.toString()
        } catch (e: ClassNotFoundException) {
            return "Class not found: $className"
        }
    }
}

