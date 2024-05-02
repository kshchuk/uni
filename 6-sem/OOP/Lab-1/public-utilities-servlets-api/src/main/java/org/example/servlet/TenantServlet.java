package org.example.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.log4j.Logger;
import org.example.dto.RequestDTO;
import org.example.entity.Request;
import org.example.mapper.RequestMapper;
import org.example.repository.TenantRepository;
import org.example.repository.impl.TenantRepositoryImpl;
import org.example.service.TenantService;
import org.example.service.impl.TenantServiceImpl;
import org.example.dto.TenantDTO;
import org.example.entity.Tenant;
import org.example.mapper.TenantMapper;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.UUID;

@WebServlet(name = "TenantServlet", value = "/tenant*")
public class TenantServlet extends HttpServlet {
    Logger logger = Logger.getLogger(TenantServlet.class.getName());
    ObjectMapper objectMapper = new ObjectMapper();
    private TenantService tenantService;

    public void init() {
        TenantRepository tenantRepository = new TenantRepositoryImpl();
        tenantService = new TenantServiceImpl(tenantRepository);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        logger.info("GET request to TenantServlet" + request.getPathInfo());

        String pathInfo = request.getPathInfo();
        if (pathInfo != null) {
            // Handle the case for "GET /tenant/all"
            if (pathInfo.equals("/all")) {
                List<Tenant> tenants = tenantService.getAll();

                List<TenantDTO> tenantDTOs = tenants.stream()
                        .map(TenantMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(tenantDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);


            // Handle the case for GET /tenant/requests?id=...
            } else if (pathInfo.startsWith("/requests")) {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                Tenant tenant = tenantService.get(UUID.fromString(id));
                if (tenant == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                List<Request> requests = tenantService.getTenantRequests(tenant.getTenantId());
                List<RequestDTO> requestDTOs = requests.stream()
                        .map(RequestMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(requestDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }


            // Handle the case for GET /tenant?id=...
            else {
                String id = request.getParameter("id");

                Tenant tenant = tenantService.get(UUID.fromString(id));

                if (tenant == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                TenantDTO tenantDTO = TenantMapper.INSTANCE.toDto(tenant);

                String jsonResponse = objectMapper.writeValueAsString(tenantDTO);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }
        }
        else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("POST request to TenantServlet" + request.getPathInfo());

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        TenantDTO tenantDTO;
        try {
            tenantDTO = objectMapper.readValue(body, TenantDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }
        Tenant tenant = TenantMapper.INSTANCE.toEntity(tenantDTO);
        tenantService.create(tenant);

        response.setStatus(HttpServletResponse.SC_CREATED);
    }

    public void doDelete(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String pathInfo = request.getPathInfo();
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("PUT request to SpecialistServlet" + body);

        if (pathInfo != null) {
            String id = request.getParameter("id");

            if (id == null) {
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                return;
            }

            boolean isDeleted = tenantService.delete(UUID.fromString(id));
            if (isDeleted) {
                response.setStatus(HttpServletResponse.SC_OK);
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        }
        else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPut(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("PUT request to TenantServlet" + body);

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        TenantDTO tenantDTO;
        try {
            tenantDTO = objectMapper.readValue(body, TenantDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        Tenant tenant = TenantMapper.INSTANCE.toEntity(tenantDTO);
        Tenant oldTenant = tenantService.get(UUID.fromString(tenantDTO.getTenantId()));
        if (oldTenant == null) {
            tenantService.create(tenant);
            response.setStatus(HttpServletResponse.SC_CREATED);
        } else {
            tenantService.update(tenant);
            response.setStatus(HttpServletResponse.SC_OK);
        }
    }
}
