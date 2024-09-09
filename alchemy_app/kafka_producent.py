from kafka import KafkaProducer
import json


def test():
        producer = KafkaProducer(
            bootstrap_servers=['kafka1.int.media-press.tv:9092'],
            value_serializer=lambda m: json.dumps(m).encode('utf-8')
        )
        return producer



def send(producer, mes, key, headers):
    if isinstance(key, int):
        k = str(key).encode('utf-8') 
    else:
        k = key.encode('utf-8') 
    
    producer.send('staz', value=mes, key=k, headers=headers)
    producer.flush()



if __name__ == "__main__":
    test()

