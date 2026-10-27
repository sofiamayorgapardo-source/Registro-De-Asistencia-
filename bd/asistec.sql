-- MariaDB dump 10.19  Distrib 10.4.32-MariaDB, for Win64 (AMD64)
--
-- Host: localhost    Database: asistec
-- ------------------------------------------------------
-- Server version	10.4.32-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `acudiente`
--

DROP TABLE IF EXISTS `acudiente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `acudiente` (
  `Acu_CodAcudiente` int(11) NOT NULL,
  `Acu_TipoDocumento` int(10) DEFAULT NULL,
  `Acu_Nombre` varchar(50) NOT NULL,
  `Acu_Apellido` varchar(50) NOT NULL,
  `Acu_Parentesco` varchar(15) NOT NULL,
  `Acu_Telefono` int(11) DEFAULT NULL,
  `Acu_Correo` varchar(30) NOT NULL,
  `Acu_Direcion` varchar(50) NOT NULL,
  PRIMARY KEY (`Acu_CodAcudiente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acudiente`
--

LOCK TABLES `acudiente` WRITE;
/*!40000 ALTER TABLE `acudiente` DISABLE KEYS */;
/*!40000 ALTER TABLE `acudiente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `arl`
--

DROP TABLE IF EXISTS `arl`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `arl` (
  `Arl_CodArl` int(11) NOT NULL,
  `Arl_Nombre` varchar(50) NOT NULL,
  `Arl_Direcion` varchar(30) NOT NULL,
  `Arl_Telefono` int(11) DEFAULT NULL,
  `Arl_Correo` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Arl_CodArl`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `arl`
--

LOCK TABLES `arl` WRITE;
/*!40000 ALTER TABLE `arl` DISABLE KEYS */;
/*!40000 ALTER TABLE `arl` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `asignatura`
--

DROP TABLE IF EXISTS `asignatura`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `asignatura` (
  `Asi_CodAsignatura` int(11) NOT NULL,
  `Asi_NomAsignatura` varchar(50) NOT NULL,
  PRIMARY KEY (`Asi_CodAsignatura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `asignatura`
--

LOCK TABLES `asignatura` WRITE;
/*!40000 ALTER TABLE `asignatura` DISABLE KEYS */;
/*!40000 ALTER TABLE `asignatura` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `docentes`
--

DROP TABLE IF EXISTS `docentes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `docentes` (
  `Doc_CodDocentes` int(11) NOT NULL,
  `Doc_TipoDocumento` int(11) DEFAULT NULL,
  `Doc_Nombres` varchar(50) NOT NULL,
  `Doc_Apellidos` varchar(50) NOT NULL,
  `Doc_FechaNacimiento` varchar(15) NOT NULL,
  `Doc_Cod_Asignatura` int(11) DEFAULT NULL,
  `Doc_Telefono` int(11) DEFAULT NULL,
  `Doc_Correo` varchar(30) NOT NULL,
  `Doc_Direcion` varchar(50) NOT NULL,
  `Doc_Obcervacion` varchar(50) NOT NULL,
  `Doc_Genero` varchar(15) NOT NULL,
  PRIMARY KEY (`Doc_CodDocentes`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `docentes`
--

LOCK TABLES `docentes` WRITE;
/*!40000 ALTER TABLE `docentes` DISABLE KEYS */;
INSERT INTO `docentes` VALUES (1,NULL,'Juan','Valdez','1985-04-10',NULL,NULL,'juan.valdez@asistec.edu','Calle 50 # 10-20','Docente titular','Masculino');
/*!40000 ALTER TABLE `docentes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eps`
--

DROP TABLE IF EXISTS `eps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `eps` (
  `Eps_CodEps` int(11) NOT NULL,
  `Eps_Nombre` varchar(50) NOT NULL,
  `Eps_Telefono` int(11) DEFAULT NULL,
  `Eps_Direcion` varchar(30) NOT NULL,
  PRIMARY KEY (`Eps_CodEps`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eps`
--

LOCK TABLES `eps` WRITE;
/*!40000 ALTER TABLE `eps` DISABLE KEYS */;
/*!40000 ALTER TABLE `eps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `estudiantes`
--

DROP TABLE IF EXISTS `estudiantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `estudiantes` (
  `Est_CodEstudiante` int(11) NOT NULL,
  `Est_Cod_TipoDocumentos` int(11) DEFAULT NULL,
  `Est_Nombre` varchar(50) NOT NULL,
  `Est_Apellido` varchar(50) NOT NULL,
  `Est_FechaDeNacimiento` varchar(15) NOT NULL,
  `Est_Cod_Grado` int(10) DEFAULT NULL,
  `Est_Cod_Grupo` int(10) DEFAULT NULL,
  `Est_Correo` varchar(30) NOT NULL,
  `Est_Telefono` int(11) DEFAULT NULL,
  `Est_Direcion` varchar(30) NOT NULL,
  `Est_Cod_Eps` int(11) DEFAULT NULL,
  `Est_ObservacionMedica` varchar(100) NOT NULL,
  `Est_Cod_ArlEstudiantil` int(11) DEFAULT NULL,
  `Est_Cod_SedeEstudiantil` int(11) DEFAULT NULL,
  `Est_estrato` int(10) DEFAULT NULL,
  `Est_Gereno` varchar(20) NOT NULL,
  `Est_Cod_Acudiente` int(11) DEFAULT NULL,
  `Est_Cod_PadresFamilia` int(11) DEFAULT NULL,
  PRIMARY KEY (`Est_CodEstudiante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `estudiantes`
--

LOCK TABLES `estudiantes` WRITE;
/*!40000 ALTER TABLE `estudiantes` DISABLE KEYS */;
INSERT INTO `estudiantes` VALUES (101,NULL,'Carlos','Perez','2008-05-12',1,1,'carlos@asistec.edu',300123456,'Calle 10 # 5-20',NULL,'Ninguna',NULL,NULL,2,'Masculino',NULL,NULL),(102,NULL,'Maria','Gomez','2008-08-20',1,1,'maria@asistec.edu',300654321,'Carrera 15 # 8-30',NULL,'Ninguna',NULL,NULL,3,'Femenino',NULL,NULL),(103,NULL,'Andres','Rodriguez','2008-11-05',1,1,'andres@asistec.edu',300987654,'Calle 20 # 4-10',NULL,'Ninguna',NULL,NULL,2,'Masculino',NULL,NULL),(201,NULL,'Laura','Sanchez','2007-03-15',2,2,'laura@asistec.edu',300555123,'Carrera 7 # 12-40',NULL,'Ninguna',NULL,NULL,3,'Femenino',NULL,NULL);
/*!40000 ALTER TABLE `estudiantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grado`
--

DROP TABLE IF EXISTS `grado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `grado` (
  `Gra_Codigo` int(11) NOT NULL,
  `Gra_NombreGrado` varchar(50) NOT NULL,
  PRIMARY KEY (`Gra_Codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grado`
--

LOCK TABLES `grado` WRITE;
/*!40000 ALTER TABLE `grado` DISABLE KEYS */;
INSERT INTO `grado` VALUES (1,'10░'),(2,'11░');
/*!40000 ALTER TABLE `grado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `grupo`
--

DROP TABLE IF EXISTS `grupo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `grupo` (
  `Gru_Codigo` int(11) NOT NULL,
  `Gru_NombreGrupo` varchar(50) NOT NULL,
  PRIMARY KEY (`Gru_Codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `grupo`
--

LOCK TABLES `grupo` WRITE;
/*!40000 ALTER TABLE `grupo` DISABLE KEYS */;
INSERT INTO `grupo` VALUES (1,'A'),(2,'B');
/*!40000 ALTER TABLE `grupo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registroasistencia`
--

DROP TABLE IF EXISTS `registroasistencia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registroasistencia` (
  `Reg_CodRegistroAsistencia` int(11) NOT NULL AUTO_INCREMENT,
  `Reg_CodEstudiante` int(11) DEFAULT NULL,
  `Reg_CodDocente` int(11) DEFAULT NULL,
  `Reg_FechaHoraIngreso` varchar(30) NOT NULL,
  `Reg_Observacion` varchar(30) NOT NULL,
  PRIMARY KEY (`Reg_CodRegistroAsistencia`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registroasistencia`
--

LOCK TABLES `registroasistencia` WRITE;
/*!40000 ALTER TABLE `registroasistencia` DISABLE KEYS */;
INSERT INTO `registroasistencia` VALUES (1,101,1,'2026-09-01 08:00:00','Presente'),(2,102,1,'2026-09-01 08:00:00','Ausente'),(3,103,1,'2026-09-01 08:00:00','Tarde');
/*!40000 ALTER TABLE `registroasistencia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registropadresfamilia`
--

DROP TABLE IF EXISTS `registropadresfamilia`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registropadresfamilia` (
  `Reg_CodPadresFamilia` int(11) NOT NULL,
  `Reg_TipoDeDocumento` int(11) DEFAULT NULL,
  `Reg_Nombres` varchar(50) NOT NULL,
  `Reg_Apellidos` varchar(50) NOT NULL,
  `Reg_Telefono` int(11) DEFAULT NULL,
  `Reg_Correo` varchar(30) NOT NULL,
  `Reg_Direccion` varchar(30) NOT NULL,
  `Reg_EmpresaTrabajo` varchar(50) NOT NULL,
  `Reg_Genero` varchar(15) NOT NULL,
  PRIMARY KEY (`Reg_CodPadresFamilia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registropadresfamilia`
--

LOCK TABLES `registropadresfamilia` WRITE;
/*!40000 ALTER TABLE `registropadresfamilia` DISABLE KEYS */;
/*!40000 ALTER TABLE `registropadresfamilia` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sedes`
--

DROP TABLE IF EXISTS `sedes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sedes` (
  `Sed_CodigoSede` int(11) NOT NULL,
  `Sed_NomSede` varchar(50) NOT NULL,
  `Sed_Direccion` varchar(30) NOT NULL,
  `Sed_Correo` varchar(30) NOT NULL,
  `Sed_Telefono` int(11) DEFAULT NULL,
  PRIMARY KEY (`Sed_CodigoSede`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sedes`
--

LOCK TABLES `sedes` WRITE;
/*!40000 ALTER TABLE `sedes` DISABLE KEYS */;
/*!40000 ALTER TABLE `sedes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tipodocumento`
--

DROP TABLE IF EXISTS `tipodocumento`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tipodocumento` (
  `Tip_Codigo` int(11) NOT NULL,
  `Tip_TipoDocumento` varchar(50) NOT NULL,
  PRIMARY KEY (`Tip_Codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tipodocumento`
--

LOCK TABLES `tipodocumento` WRITE;
/*!40000 ALTER TABLE `tipodocumento` DISABLE KEYS */;
/*!40000 ALTER TABLE `tipodocumento` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `usuario` varchar(50) NOT NULL,
  `password` varchar(100) NOT NULL,
  `rol` varchar(20) NOT NULL,
  `id_docente` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'docente1','1234','docente',1),(2,'coordinador','admin123','coordinador',NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-07  7:13:26
