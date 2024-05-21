package org.example.repository.impl;

import org.apache.log4j.Logger;
import org.example.dao.RequestDao;
import org.example.dao.TenantDao;
import org.example.dao.db.DAOManager;
import org.example.entity.Request;
import org.example.entity.Tenant;
import org.example.repository.TenantRepository;

import java.util.List;
import java.util.UUID;

public class TenantRepositoryImpl implements TenantRepository {
    private Logger logger = Logger.getLogger(TenantRepositoryImpl.class);
    private TenantDao tenantDao;
    private RequestDao requestDao;

    public TenantRepositoryImpl() {
        DAOManager manager = DAOManager.getInstance();
        try {
            tenantDao = (TenantDao) manager.getDAO(DAOManager.Table.TENANT);
            requestDao = (RequestDao) manager.getDAO(DAOManager.Table.REQUEST);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void create(Tenant entity) {
        try {
            tenantDao.create(entity);
            for (Request request : entity.getRequests()) {
                var dbRequest = requestDao.read(request.getRequestId());
                if (dbRequest == null) {
                    requestDao.create(request);
                }
                else {
                    logger.info("Request with id " + request.getRequestId() + " already exists in the database.");
                }
            }
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public Tenant read(UUID uuid) {
        try {
            return tenantDao.read(uuid);
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public Tenant readWithRequests(Tenant tenant) {
        try {
            List<Request> requests = requestDao.findByTenantId(tenant.getTenantId());
            tenant.setRequests(requests);
            return tenant;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }

    @Override
    public void update(Tenant entity) {
        try {
            tenantDao.update(entity);
            if (entity.getRequests() == null) {
                return;
            }
            else {
                // Add new requests and update existing ones
                for (Request request : entity.getRequests()) {
                    var dbRequest = requestDao.read(request.getRequestId());
                    if (dbRequest == null) {
                        requestDao.create(request);
                    }
                    else {
                        requestDao.update(request);
                    }
                }

//                // remove requests that are not in the updated entity
//                List<Request> dbRequests = requestDao.findByTenantId(entity.getTenantId());
//                for (Request dbRequest : dbRequests) {
//                    if (!entity.getRequests().contains(dbRequest)) {
//                        requestDao.delete(dbRequest.getRequestId());
//                    }
//                }
            }
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public void delete(UUID uuid) {
        try {
            tenantDao.delete(uuid);
        } catch (Exception e) {
            logger.error(e);
        }
    }

    @Override
    public List<Tenant> findAll() {
        try {
            List<Tenant> tenants = tenantDao.findAll();
            return tenants;
        } catch (Exception e) {
            logger.error(e);
            return null;
        }
    }
}
