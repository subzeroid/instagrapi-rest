package main

import (
  "fmt"
  "io/ioutil"
  "net/http"
)

const BaseUrl = "http://localhost:8000"

func main() {
  resp, err := http.Get(fmt.Sprintf("%s/version", BaseUrl))
  if err != nil {
    fmt.Println(err)
  }
  defer resp.Body.Close()
  body, err := ioutil.ReadAll(resp.Body)
  fmt.Printf("\nVersion: %s", string(body))
}
