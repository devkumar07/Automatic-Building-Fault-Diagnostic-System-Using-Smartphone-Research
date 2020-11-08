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

class ViewController: UIViewController, UITextFieldDelegate {
    
    let bucketName = "faultdetect"
    
    @IBOutlet weak var areaField: UITextField!
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        areaField.delegate = self
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
            }
            
            return nil
        }
    }

    @IBAction func uploadReading(_ sender: Any) {
        uploadFile(with: "sensor_data", type: "csv")
    }
    
    @IBAction func predictButton(_ sender: Any) {
       areaField.endEditing(true)
       let parameters = ["area": areaField.text]
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
               } catch {
                   print(error)
               }
           }
           
       }.resume()
    }
    
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        areaField.endEditing(true)
        return true
    }
    
}

