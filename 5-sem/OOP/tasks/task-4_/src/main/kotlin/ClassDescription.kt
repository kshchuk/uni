import kotlin.reflect.full.memberFunctions
import kotlin.reflect.full.memberProperties
import kotlin.reflect.jvm.kotlinProperty


/**
 * A utility class for describing the structure of a Java class using reflection.
 */
class ClassDescription {
    private val customClassLoader = CustomClassLoader()
    /**
     * Get a complete description of a class with the given name, including information about
     * properties, fields, and methods.
     *
     * @param className The fully qualified class name to be described.
     * @return A string containing the class description.
     */
    fun describeClass(className: String): String {
        try {
            val clazz = customClassLoader.findClass(className);
            val classInfo = StringBuilder()

            classInfo.append("Class Name: ${clazz.simpleName}\n")
            classInfo.append("Package: ${clazz.`package`?.name}\n")

            val kClazz = clazz.kotlin
            val properties = kClazz.memberProperties
            val fields = clazz.fields
            val functions = kClazz.memberFunctions

            classInfo.append("\nProperties:\n")
            for (property in properties) {
                classInfo.append("${property.visibility} ${property.name}: ${property.returnType}\n")
            }

            classInfo.append("\nFields:\n")
            for (field in fields) {
                classInfo.append("${field.kotlinProperty}  ${field.name}: ${field.type}\n")
            }

            classInfo.append("\nMethods:\n")
            for (function in functions) {
                classInfo.append("${function.visibility} ${function.name}(${function.parameters.joinToString { "${it.name}: ${it.type}" }}): ${function.returnType}\n")
            }

            classInfo.append("\nInheritance Hierarchy:\n")
            var superClass = clazz.superclass
            while (superClass != null) {
                classInfo.append("${superClass.name}\n")
                superClass = superClass.superclass
            }

            classInfo.append("\nInterfaces:\n")
            for (interfac in clazz.interfaces) {
                classInfo.append("${interfac.name}\n")
            }

            return classInfo.toString()
        } catch (e: ClassNotFoundException) {
            return "Class not found: $className"
        }
    }

}
