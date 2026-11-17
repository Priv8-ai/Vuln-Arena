FROM ruby:3.3-alpine
WORKDIR /app
RUN gem install sinatra:3.2.0 rack:2.2.9 webrick --no-document
COPY app.rb .
COPY static ./static
RUN mkdir -p /app/posts /app/uploads && echo 'draft secret ARENA{ink_draft_file}' > /app/posts/.draft.md \
 && echo 'Ink posts directory' > /app/posts/README.md
EXPOSE 80
CMD ["ruby", "app.rb"]
