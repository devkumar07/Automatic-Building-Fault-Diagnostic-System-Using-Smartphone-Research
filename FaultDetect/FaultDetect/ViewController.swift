//
//  ViewController.swift
//  FaultDetect
//
//  Created by Devanshu Kumar on 11/1/20.
//

import UIKit
import AVKit
import AVFoundation
import AWSCognito
import AWSS3

struct Response: Decodable {
    let error: Int
    let msg: String
}

class ViewController: UIViewController, UITextFieldDelegate {
    
    let bucketName = "faultdetect"
    @IBOutlet weak var timeStepsField: UITextField!
    @IBOutlet weak var areaField: UITextField!
    @IBOutlet weak var filenameField: UITextField!
    @IBOutlet weak var resultLabel: UILabel!
    @IBOutlet weak var successSensorDataUpload: UILabel!
    @IBOutlet weak var zoneTempField: UITextField!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        areaField.delegate = self
        timeStepsField.delegate = self
        // Do any additional setup after loading the view.
        // Initialize the Amazon Cognito credentials provider

        let credentialsProvider = AWSCognitoCredentialsProvider(regionType:.USWest2,
           identityPoolId:"us-west-2:5c2d5414-e63d-4114-b5bc-c21ee68babff")

        let configuration = AWSServiceConfiguration(region:.USWest2, credentialsProvider:credentialsProvider)

        AWSServiceManager.default().defaultServiceConfiguration = configuration
    }
    
    func uploadFile(with resource: String, type: String){
        let key = "\(resource).\(type)"
        let localFilePath = Bundle.main.path(forResource: resource, ofType: type)!
        let localFileUrl = URL(fileURLWithPath: localFilePath)
        
        let request = AWSS3TransferManagerUploadRequest()!
        request.bucket = bucketName
        request.key = key
        request.body = localFileUrl
        request.acl = .publicReadWrite
        
        let transferManager = AWSS3TransferManager.default()
        transferManager.upload(request).continueWith(executor: AWSExecutor.mainThread()) { (task) -> Any? in
            if let error = task.error{
                print(error)
            }
            if task.result != nil{
                print("Uploaded \(key)")
                DispatchQueue.main.async {
                    self.resultLabel.text = "Sensor data uploaded!"
                }
            }
            
            return nil
        }
    }

    @IBAction func uploadReading(_ sender: Any) {
        uploadFile(with: (filenameField.text)!, type: "csv")
    }
    @IBAction func uploadZoneTemp(_ sender: Any) {
        uploadFile(with: (zoneTempField.text)!, type: "csv")
    }
    
    @IBAction func predictButton(_ sender: Any) {
       areaField.endEditing(true)
       let parameters = ["area": areaField.text,"file_name": filenameField.text]
       guard let url = URL(string: "http://127.0.0.1:5000/predict") else { return }
       var request = URLRequest(url: url)
       request.httpMethod = "POST"
       request.addValue("application/json", forHTTPHeaderField: "Content-Type")
       guard let httpBody = try? JSONSerialization.data(withJSONObject: parameters, options: []) else { return }
       request.httpBody = httpBody
       
       let session = URLSession.shared
       session.dataTask(with: request) { (data, response, error) in
           if let response = response {
            print(response)
           }
           
           if let data = data {
               do {
                   let json = try JSONSerialization.jsonObject(with: data, options: [])
                   print(json)
                    let response = try JSONDecoder().decode(Response.self, from: data)
                    DispatchQueue.main.async {
                        self.resultLabel.text = response.msg
                    }
               } catch {
                   print(error)
               }
           }
           
       }.resume()
    }
    
    @IBAction func recordTempButton(_ sender: Any) {
        areaField.endEditing(true)
        let parameters = ["steps": timeStepsField.text]
        guard let url = URL(string: "http://127.0.0.1:5000/getOutsideTemp") else { return }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        guard let httpBody = try? JSONSerialization.data(withJSONObject: parameters, options: []) else { return }
        request.httpBody = httpBody
        DispatchQueue.main.async {
            self.resultLabel.text = "Recording outside tempreature"
        }
        let session = URLSession.shared
        session.dataTask(with: request) { (data, response, error) in
            if let response = response {
             print(response)
            }
            
            if let data = data {
                do {
                    let json = try JSONSerialization.jsonObject(with: data, options: [])
                    print(json)
                     let response = try JSONDecoder().decode(Response.self, from: data)
                     DispatchQueue.main.async {
                        self.resultLabel.text = response.msg
                     }
                } catch {
                    print(error)
                }
            }
            
        }.resume()
    }
    
    
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        areaField.endEditing(true)
        filenameField.endEditing(true)
        timeStepsField.endEditing(true)
        return true
    }
    
}

