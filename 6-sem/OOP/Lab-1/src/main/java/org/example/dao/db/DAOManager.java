package org.example.dao.db;

import org.apache.log4j.Logger;
import org.example.dao.CrudDao;

import java.sql. *;

public class DAOManager {
    private Logger logger = Logger.getLogger(DAOManager.class);

    public enum Table { REQUEST, SPECIALIST, TEAM, TENANT, WORKPLAN }
    public static DAOManager getInstance() {
        return DAOManagerSingleton.INSTANCE.get();
    }

    public void open() throws SQLException {
        if(this.con==null || this.con.isClosed()) {
            try {
                this.con = DriverManager.getConnection(
                        this.DATABASE_URL + "/" + this.DATABASE_NAME,
                        this.DATABASE_USER_NAME,
                        this.DATABASE_USER_PASSWORD
                );
                logger.info("Connection to database established.");
            } catch (SQLException e) {
                try {
                    Connection conn = DriverManager.getConnection(
                            this.DATABASE_URL + "/",
                            this.DATABASE_USER_NAME,
                            this.DATABASE_USER_PASSWORD
                    );
                    Statement stmt = conn.createStatement();
                    stmt.execute("CREATE DATABASE " + DATABASE_NAME);

                    this.con = DriverManager.getConnection(
                            this.DATABASE_URL + "/" + this.DATABASE_NAME,
                            this.DATABASE_USER_NAME,
                            this.DATABASE_USER_PASSWORD
                    );

                    logger.info("Database created.");
                } catch (SQLException ex) {
                    logger.error("Error creating database.", ex);
                }
            }

            return;
        }

        logger.info("Connection to database already established.");
    }

    public void close() throws SQLException {
        if(this.con!=null && !this.con.isClosed()) {
            this.con.close();
            logger.info("Connection to database closed.");
        }

        logger.info("Connection to database already closed.");
    }
    private Connection con;
    private String DATABASE_URL;
    private String DATABASE_NAME;
    private String DATABASE_USER_NAME;
    private String DATABASE_USER_PASSWORD;
    private DAOManager() throws Exception {
        Class.forName("org.postgresql.Driver").newInstance();

        System.getenv().forEach((k, v) -> {
            switch (k) {
                case "DATABASE_URL" -> this.DATABASE_URL = v;
                case "DATABASE_NAME" -> this.DATABASE_NAME = v;
                case "DATABASE_USER_NAME" -> this.DATABASE_USER_NAME = v;
                case "DATABASE_USER_PASSWORD" -> this.DATABASE_USER_PASSWORD = v;
            }
        });

        if(this.DATABASE_URL == null || this.DATABASE_NAME == null ||
                this.DATABASE_USER_NAME == null || this.DATABASE_USER_PASSWORD == null)
            throw new Exception("Environment variables not set.");
        this.init();
    }

    private static class DAOManagerSingleton {

        public static final ThreadLocal<DAOManager> INSTANCE;
        static
        {
            ThreadLocal<DAOManager> dm;
            try
            {
                dm = ThreadLocal.withInitial(() -> {
                    try
                    {
                        return new DAOManager();
                    }
                    catch(Exception e)
                    {
                        Logger.getLogger(DAOManager.class).error("Error creating DAOManager instance.", e);
                        return null;
                    }
                });
            }
            catch(Exception e) { dm = null; }
            INSTANCE = dm;
        }

    }

    public CrudDao getDAO(Table t) throws SQLException
    {
        if(this.con == null || this.con.isClosed()) //Let's ensure our connection is open
            this.open();

        return switch (t) {
            case REQUEST -> new RequestDBDao(this.con, "request");
            case SPECIALIST -> new SpecialistDBDao(this.con, "specialist");
            case TEAM -> new TeamDBDao(this.con, "team");
            case TENANT -> new TenantDBDao(this.con, "tenant");
            case WORKPLAN -> new WorkPlanDBDao(this.con, "work_plan");
            default -> throw new SQLException("Trying to link to an unexistant table.");
        };

    }

    private void init() throws SQLException {
        if(this.con == null || this.con.isClosed()) // Let's ensure our connection is open
            this.open();
    }
}