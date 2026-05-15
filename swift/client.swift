#!/usr/bin/swift
//
//  client.swift
//  for aiograpi-rest
//
//

import Foundation

let BaseUrl = "http://localhost:8000"

func getDeps() {
    let url = URL(string: "\(BaseUrl)/deps")!
    let sem = DispatchSemaphore(value: 0)
    let task = URLSession.shared.dataTask(with: url) {(data, response, error) in
        guard let data = data else { return }
        print("\nDependencies:", String(data: data, encoding: .utf8)!)
        sem.signal()
    }
    task.resume()
    sem.wait()
}

//func pkFromCode(code: String) {
//    // let url = URL(string: "\(BaseUrl)/media/pk_from_code")!
//    let queryItems = URLQueryItem(name: "code", value: code)
//    var urlComps = URLComponents(string: "\(BaseUrl)/media/pk_from_code")
//    urlComps.queryItems = queryItems
//    let url = urlComps.url!
//    let sem = DispatchSemaphore(value: 0)
//    let task = URLSession.shared.dataTask(with: url) {(data, response, error) in
//        guard let data = data else { return }
//        print("\npkFromCode: \(code) ->", String(data: data, encoding: .utf8)!)
//        sem.signal()
//    }
//    task.resume()
//    sem.wait()
//}

getDeps()
//pkFromCode(code: "B1LbfVPlwIA")
// dump(Process.arguments)
