package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

const BaseUrl = "http://localhost:8000"

func getVersion() string {
	resp, err := http.Get(fmt.Sprintf("%s/version", BaseUrl))
	if err != nil {
		fmt.Println(err)
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	return string(body)
}

func pkFromCode(code string) string {
	client := &http.Client{}
	req, _ := http.NewRequest(
		"GET",
		fmt.Sprintf("%s/media/pk_from_code", BaseUrl),
		nil,
	)
	q := req.URL.Query()
	q.Add("code", code)
	req.URL.RawQuery = q.Encode()
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println(err)
	}
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println(err)
	}
	return string(body)
}

func login(username string, password string) string {
	client := &http.Client{}
	data := url.Values{}
	data.Set("username", username)
	data.Set("password", password)
	req, _ := http.NewRequest(
		"GET",
		fmt.Sprintf("%s/auth/login", BaseUrl),
		strings.NewReader(data.Encode()),
	)
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	req.Header.Add("Content-Length", strconv.Itoa(len(data.Encode())))
	resp, _ := client.Do(req)
	defer resp.Body.Close()
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println(err)
	}
	return string(body)
}

func main() {
	fmt.Printf("\nVersion: %s", getVersion())
	fmt.Printf("\npkFromCode: B1LbfVPlwIA -> %s", pkFromCode("B1LbfVPlwIA"))
	sessionid := login("adw0rd", "test")
	fmt.Printf("\nSESSIONID: %s", sessionid)
}
