-- =========================================================================
-- ASISTEC - Esquema y Estructura de Base de Datos (18 Tablas Oficiales)
-- Proyecto: Sistema Inteligente de Registro de Asistencia Estudiantil
-- Nota: Este archivo contiene únicamente la estructura DDL y catálogos
--       iniciales del sistema. NO CONTIENE datos personales ni contraseñas.
-- =========================================================================
--
-- Estructura de tabla para `acudiente`
--
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
--
-- Estructura de tabla para `arl`
--
CREATE TABLE `arl` (
  `Arl_CodArl` int(11) NOT NULL,
  `Arl_Nombre` varchar(50) NOT NULL,
  `Arl_Direcion` varchar(30) NOT NULL,
  `Arl_Telefono` int(11) DEFAULT NULL,
  `Arl_Correo` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Arl_CodArl`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `asignatura`
--
CREATE TABLE `asignatura` (
  `Asi_CodAsignatura` int(11) NOT NULL,
  `Asi_NomAsignatura` varchar(50) NOT NULL,
  PRIMARY KEY (`Asi_CodAsignatura`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Catálogo inicial para `asignatura`
--
INSERT INTO `asignatura` VALUES (1,'Tecnología e Informática'),(2,'Ciencias Naturales'),(3,'Inglés'),(4,'Matemáticas'),(5,'Lengua Castellana'),(6,'Química'),(7,'Educación Artística'),(8,'Educación Religiosa'),(9,'Emprendimiento'),(10,'Ética y Valores'),(11,'Sociales'),(12,'Física'),(13,'Filosofía'),(14,'Contabilidad'),(15,'Ciencias Económicas y Políticas'),(16,'Educación Física');
--
-- Estructura de tabla para `configuracion_sistema`
--
CREATE TABLE `configuracion_sistema` (
  `clave` varchar(50) NOT NULL,
  `valor` varchar(100) NOT NULL,
  PRIMARY KEY (`clave`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Catálogo inicial para `configuracion_sistema`
--
INSERT INTO `configuracion_sistema` VALUES ('anio_lectivo_activo','2026'),('permiso_docentes_tecnologia','0');
--
-- Estructura de tabla para `docente_areas`
--
CREATE TABLE `docente_areas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_docente` int(11) NOT NULL,
  `id_area` int(11) NOT NULL,
  `es_principal` tinyint(1) DEFAULT 0,
  `es_jefe` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_docente_area` (`id_docente`,`id_area`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `docente_asignaturas`
--
CREATE TABLE `docente_asignaturas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_docente` int(11) NOT NULL,
  `id_asignatura` int(11) NOT NULL,
  `es_principal` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_docente_asig` (`id_docente`,`id_asignatura`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `docentes`
--
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
--
-- Estructura de tabla para `eps`
--
CREATE TABLE `eps` (
  `Eps_CodEps` int(11) NOT NULL,
  `Eps_Nombre` varchar(50) NOT NULL,
  `Eps_Telefono` int(11) DEFAULT NULL,
  `Eps_Direcion` varchar(30) NOT NULL,
  PRIMARY KEY (`Eps_CodEps`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `estudiantes`
--
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
  `Est_Jornada` varchar(20) DEFAULT 'Mañana',
  `Est_Estado` varchar(20) DEFAULT 'Activo',
  `Est_AnioLectivo` int(11) DEFAULT 2026,
  PRIMARY KEY (`Est_CodEstudiante`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `grado`
--
CREATE TABLE `grado` (
  `Gra_Codigo` int(11) NOT NULL,
  `Gra_NombreGrado` varchar(50) NOT NULL,
  PRIMARY KEY (`Gra_Codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Catálogo inicial para `grado`
--
INSERT INTO `grado` VALUES (0,'Transición'),(1,'1'),(2,'2'),(3,'3'),(4,'4'),(5,'5'),(6,'6'),(7,'7'),(8,'8'),(9,'9'),(10,'10'),(11,'11');
--
-- Estructura de tabla para `grupo`
--
CREATE TABLE `grupo` (
  `Gru_Codigo` int(11) NOT NULL,
  `Gru_NombreGrupo` varchar(50) NOT NULL,
  `Gru_Cod_Grado` int(11) DEFAULT NULL,
  PRIMARY KEY (`Gru_Codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Catálogo inicial para `grupo`
--
INSERT INTO `grupo` VALUES (1,'1-1',1),(2,'1-2',1),(3,'Transición',0),(21,'2-1',2),(22,'2-2',2),(31,'3-1',3),(32,'3-2',3),(41,'4-1',4),(42,'4-2',4),(51,'5-1',5),(52,'5-2',5),(53,'5-3',5),(61,'6-1',6),(62,'6-2',6),(63,'6-3',6),(64,'6-4',6),(65,'6-5',6),(71,'7-1',7),(72,'7-2',7),(73,'7-3',7),(74,'7-4',7),(75,'7-5',7),(76,'7-6',7),(81,'8-1',8),(82,'8-2',8),(83,'8-3',8),(84,'8-4',8),(85,'8-5',8),(86,'8-6',8),(87,'8-7',8),(91,'9-1',9),(92,'9-2',9),(93,'9-3',9),(94,'9-4',9),(95,'9-5',9),(101,'10-1',10),(102,'10-2',10),(103,'10-3',10),(104,'10-4',10),(105,'10-5',10),(106,'10-6',10),(111,'11-1',11),(112,'11-2',11),(113,'11-3',11),(114,'11-4',11),(115,'11-5',11),(116,'11-6',11);
--
-- Estructura de tabla para `historial_actualizaciones_matricula`
--
CREATE TABLE `historial_actualizaciones_matricula` (
  `id_actualizacion` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_actualizacion` datetime DEFAULT current_timestamp(),
  `anio_academico` int(11) NOT NULL,
  `usuario` varchar(100) NOT NULL,
  `total_cargados` int(11) NOT NULL DEFAULT 0,
  `estudiantes_nuevos` int(11) NOT NULL DEFAULT 0,
  `estudiantes_actualizados` int(11) NOT NULL DEFAULT 0,
  `estudiantes_retirados` int(11) NOT NULL DEFAULT 0,
  `errores` int(11) NOT NULL DEFAULT 0,
  `nombre_archivo` varchar(255) DEFAULT '',
  `detalles` text DEFAULT NULL,
  PRIMARY KEY (`id_actualizacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `historial_matricula_estudiantes`
--
CREATE TABLE `historial_matricula_estudiantes` (
  `id_historial` int(11) NOT NULL AUTO_INCREMENT,
  `id_estudiante` int(11) NOT NULL,
  `anio_lectivo` int(11) NOT NULL,
  `grado_id` int(11) NOT NULL,
  `grupo_id` int(11) NOT NULL,
  `jornada` varchar(30) DEFAULT 'Mañana',
  `sede_id` int(11) DEFAULT 1,
  `estado` varchar(20) DEFAULT 'Activo',
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id_historial`),
  KEY `idx_est_anio` (`id_estudiante`,`anio_lectivo`),
  KEY `idx_anio_grado_grupo` (`anio_lectivo`,`grado_id`,`grupo_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `registroasistencia`
--
CREATE TABLE `registroasistencia` (
  `Reg_CodRegistroAsistencia` int(11) NOT NULL AUTO_INCREMENT,
  `Reg_CodEstudiante` int(11) DEFAULT NULL,
  `Reg_CodDocente` int(11) DEFAULT NULL,
  `Reg_FechaHoraIngreso` varchar(30) NOT NULL,
  `Reg_Observacion` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Reg_Jornada` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'Mañana',
  `Reg_Sede` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT 'Sede Central',
  `Reg_Asignatura` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`Reg_CodRegistroAsistencia`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `registropadresfamilia`
--
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
--
-- Estructura de tabla para `sedes`
--
CREATE TABLE `sedes` (
  `Sed_CodigoSede` int(11) NOT NULL,
  `Sed_NomSede` varchar(50) NOT NULL,
  `Sed_Direccion` varchar(30) NOT NULL,
  `Sed_Correo` varchar(30) NOT NULL,
  `Sed_Telefono` int(11) DEFAULT NULL,
  PRIMARY KEY (`Sed_CodigoSede`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Catálogo inicial para `sedes`
--
INSERT INTO `sedes` VALUES (1,'Sede Central','Calle 50 # 10-20','central@asistec.edu',6012345),(2,'San Francisco','Carrera 15 # 40-12','sanfrancisco@asistec.edu',6012346),(3,'Secundino Porras','Avenida 6 # 25-18','secundino@asistec.edu',6012347),(4,'Sede Picaleña','Sector Picaleña Km 3','picalena@asistec.edu',6012348),(5,'Sede Arboleda','Calle 70 # 18-30','arboleda@asistec.edu',6012349),(6,'Bellorizonte','Diagonal 45 # 12-05','bellorizonte@asistec.edu',6012350),(7,'San Martín','Carrera 8 # 32-15','sanmartin@asistec.edu',6012351);
--
-- Estructura de tabla para `tipodocumento`
--
CREATE TABLE `tipodocumento` (
  `Tip_Codigo` int(11) NOT NULL,
  `Tip_TipoDocumento` varchar(50) NOT NULL,
  PRIMARY KEY (`Tip_Codigo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
--
-- Estructura de tabla para `usuarios`
--
CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `usuario` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol` varchar(20) NOT NULL,
  `id_docente` int(11) DEFAULT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `estado` varchar(20) NOT NULL DEFAULT 'Activo',
  `permiso_matricula` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `usuario` (`usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
-- =========================================================================
-- Fin de estructura de tablas
-- =========================================================================
