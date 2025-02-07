package rqueue

import (
  "fmt"
  "os"
  "github.com/joho/godotenv"
  "log"
  "context"
  "github.com/redis/go-redis/v9"
)

var ctx = context.Background()

func init() {
    // loads values from .env into the system
    if err := godotenv.Load(); err != nil {
        log.Print("No .env file found")
    }
}

func RedisCli() *redis.Client {
  redis_url := os.Getenv("REDIS_URL")


  if (redis_url == "") {
    log.Fatal("SET REDIS WTF")
  }

  fmt.Println("we are cool here ", redis_url)


  opts, err := redis.ParseURL(redis_url)
  if err != nil {
      panic(err)
  }

  return redis.NewClient(opts)
}

