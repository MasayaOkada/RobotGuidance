import chainer
import chainer.functions as F
import chainer.links as L
from chainer import Chain, variable
from chainer.datasets import TupleDataset
from chainer.iterators import SerialIterator
import numpy as np
import matplotlib as plt
import os
from os.path import expanduser

# HYPER PARAM
NUM_EPISODE = 100
BATCH_SIZE = 32

class Net(chainer.Chain):
    def __init__(self, n_channel=3, n_action=3):
        initializer = chainer.initializers.HeNormal()
        super(Net, self).__init__(
            conv1=L.Convolution2D(n_channel, 32, ksize=8, stride=4, nobias=False, initialW=initializer),
            conv2=L.Convolution2D(32, 64, ksize=3, stride=2, nobias=False, initialW=initializer),
            conv3=L.Convolution2D(64, 64, ksize=3, stride=1, nobias=False, initialW=initializer),
            conv4=L.Linear(960, 512, initialW=initializer),
            fc5=L.Linear(512, n_action, initialW=np.zeros((n_action, 512), dtype=np.int32))
        )

    def __call__(self, x, test=False):
        s = chainer.Variable(x)
        h1 = F.relu(self.conv1(s))
        h2 = F.relu(self.conv2(h1))
        h3 = F.relu(self.conv3(h2))
        h4 = F.relu(self.conv4(h3))
        h = self.fc5(h4)
        return h

class deep_learning:
    def __init__(self, n_channel=3, n_action=3):
        self.net = Net(n_channel, n_action)
        self.optimizer = chainer.optimizers.Adam(eps=1e-2)
        self.optimizer.setup(self.net)
        self.n_action = n_action
        self.phi = lambda x: x.astype(np.float32, copy=False)

    def act_and_trains(self, imgobj, correct_action, done):
      
        if done:
            x = [self.phi(s) for s in [imgobj]]
            t = np.array([correct_action], np.int32)
            dataset = TupleDataset(x, t)
            train_iter = SerialIterator(dataset, batch_size = BATCH_SIZE, repeat=True, shuffle=False)
        
            count = 1

            results_train = {}
            results_train['loss'], results_train['accuracy'] = [], []
        
            for epoch in range(NUM_EPISODE):
                train_batch  = train_iter.next()
                x_train, t_train = chainer.dataset.concat_examples(train_batch, -1)

                y_train = self.net(x_train)

                loss_train = F.softmax_cross_entropy(y_train, t_train)
                acc_train = F.accuracy(y_train, t_train)
                self.net.cleargrads()
                loss_train.backward()
                self.optimizer.update()
        
                count += 1

                results_train['loss'] .append(loss_train.array)
                results_train['accuracy'] .append(acc_train.array)

                action = np.argmax(y_train.array)
            print('epoch: {}, iteration: {}, loss (train): {:.4f}, acc (train): {:.4f}, action: {}'.format(epoch, count, loss_train.array.mean(), acc_train.array.mean(), action))
            
            return action

    def act(self, imgobj):
            x = [self.phi(s) for s in [imgobj]]
            x_test = chainer.dataset.concat_examples(x, -1)
            with chainer.using_config('train', False), chainer.using_config('enable_backprop', False):
                action_value = self.net(x_test)
                action = np.argmax(action_value.array)
            return action
                
if __name__ == '__main__':
        dl = deep_learning()
