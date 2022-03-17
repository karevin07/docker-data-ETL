name := "data-etl"

version := "0.0.1"

scalaVersion := "2.12.10"

val sparkVersion = "3.1.1"


val scalaDependency = Seq(
  "org.scalatest" %% "scalatest" % "3.0.1" % "test"
)
val sparkDependencies = Seq(
  "org.apache.spark" %% "spark-core" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql" % sparkVersion % "provided"
)

lazy val coreLib = scalaDependency ++ sparkDependencies

lazy val commonSettings = Seq(
  fork in Test := true,
  javaOptions ++= Seq("-Xms512M", "-Xmx2048M", "-XX:MaxPermSize=2048M", "-XX:+CMSClassUnloadingEnabled"),
  scalacOptions += "-target:jvm-1.8",
  testOptions in Test += Tests.Argument(TestFrameworks.ScalaTest, "-oD"),
)


lazy val app = (project in file("."))
  .settings(commonSettings: _*)
  .settings(
    libraryDependencies ++= coreLib
  ).settings(
    assemblyJarName in assembly := name.value + "-" + version.value + ".jar",
    assemblyMergeStrategy in assembly := {
      case PathList("META-INF", xs@_*) => MergeStrategy.discard
      case x => MergeStrategy.first
    }
  )


