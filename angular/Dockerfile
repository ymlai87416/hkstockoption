# production environment
FROM nginx:stable-alpine

RUN mkdir /usr/share/nginx/html/hkstockoption
COPY dist/client /usr/share/nginx/html/hkstockoption
# new
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]