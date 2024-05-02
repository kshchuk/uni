package org.example.servlet;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.example.dto.RequestDTO;
import org.example.entity.Request;
import org.example.mapper.RequestMapper;
import org.example.repository.RequestRepository;
import org.example.repository.impl.RequestRepositoryImpl;
import org.example.service.RequestService;
import org.example.service.impl.RequestServiceImpl;

import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.List;
import java.util.UUID;
import java.util.logging.Logger;

@WebServlet(name = "RequestServlet", value = "/request*")
public class RequestServlet extends HttpServlet {
    Logger logger = Logger.getLogger(SpecialistServlet.class.getName());
    ObjectMapper objectMapper = new ObjectMapper();
    private RequestService requestService;

    public void init() {
        RequestRepository requestRepository = new RequestRepositoryImpl();
        requestService = new RequestServiceImpl(requestRepository);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        PrintWriter out = response.getWriter();

        logger.info("GET request to RequestServlet" + request.getPathInfo());

        String pathInfo = request.getPathInfo();
        if (pathInfo != null) {
            // Handle the case for "GET /request/all"
            if (pathInfo.equals("/all")) {
                List<Request> requests = requestService.getAll();
                List<RequestDTO> requestDTOs = requests.stream()
                        .map(RequestMapper.INSTANCE::toDto)
                        .toList();

                String jsonResponse = objectMapper.writeValueAsString(requestDTOs);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }

            // Handle the case for GET /request/?id=...
            else {
                String id = request.getParameter("id");

                if (id == null) {
                    response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                    return;
                }

                Request requestModel = requestService.get(UUID.fromString(id));

                if (requestModel == null) {
                    response.setStatus(HttpServletResponse.SC_NOT_FOUND);
                    return;
                }

                RequestDTO requestDTO = RequestMapper.INSTANCE.toDto(requestModel);

                String jsonResponse = objectMapper.writeValueAsString(requestDTO);
                out.write(jsonResponse);

                response.setStatus(HttpServletResponse.SC_OK);
            }
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("POST request to RequestServlet" + request.getPathInfo());

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        RequestDTO requestDTO;
        try {
            requestDTO = objectMapper.readValue(body, RequestDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }
        Request requestModel = RequestMapper.INSTANCE.toEntity(requestDTO);
        requestService.create(requestModel);

        response.setStatus(HttpServletResponse.SC_CREATED);
    }

    public void doDelete(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String pathInfo = request.getPathInfo();

        logger.info("DELETE request to RequestServlet" + pathInfo);

        if (pathInfo != null) {
            String id = request.getParameter("id");

            if (id == null) {
                response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
                return;
            }

            boolean isDeleted = requestService.delete(UUID.fromString(id));
            if (isDeleted) {
                response.setStatus(HttpServletResponse.SC_OK);
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        } else {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
        }
    }

    public void doPut(HttpServletRequest request, HttpServletResponse response) throws IOException {
        response.setContentType("application/json");
        String pathInfo = request.getPathInfo();
        String body = request.getReader().lines().reduce("", (accumulator, actual) -> accumulator + actual);

        logger.info("PUT request to RequestServlet" + pathInfo);

        if (body.isEmpty()) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        RequestDTO requestDTO;
        try {
            requestDTO = objectMapper.readValue(body, RequestDTO.class);
        } catch (Exception e) {
            response.setStatus(HttpServletResponse.SC_BAD_REQUEST);
            return;
        }

        Request newRequest = RequestMapper.INSTANCE.toEntity(requestDTO);
        Request oldRequest = requestService.get(UUID.fromString(requestDTO.getRequestId()));
        if (oldRequest == null) {
            requestService.create(newRequest);
            response.setStatus(HttpServletResponse.SC_CREATED);
        } else {
            requestService.update(newRequest);
            response.setStatus(HttpServletResponse.SC_OK);
        }
    }
}
