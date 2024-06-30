<template>
  <div class="feedback-component">
    <div v-if="show" id="modal-window">
      <transition name="modal">
        <div class="modal-mask">
          <div class="modal-wrapper">
            <div class="modal-container">
              <div class="modal-header">
                <slot name="header">
                  <button class="close-button" @click="show=false;">X</button>
                </slot>
              </div>

              <div class="modal-body">
                <slot name="body">
                  Your email:
                  <input class="input-text" v-model="email"
                  placeholder="email@address.com" type="text" />
                  <textarea class="feedback-textarea"
                  v-model="message"
                  placeholder="Wishes? Comments? Give me some feedback!"></textarea>
                </slot>
              </div>

              <div class="modal-footer">
                <button class="click-button"
                @click="send();"
                :disabled="!showSendButton">Send</button>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
    <div id="feedback-button">
      <img @click="show=true;" width="30" height="30" src="message_icon.png" />
    </div>
  </div>
</template>


<style lang="css">
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: table;
  transition: opacity 0.3s ease;
}

.modal-wrapper {
  display: table-cell;
  vertical-align: middle;
}

.modal-container {
  width: 500px;
  margin: 0px auto;
  padding: 20px 30px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  transition: all 0.3s ease;
  font-family: Helvetica, Arial, sans-serif;
}

.modal-header h3 {
  margin-top: 0;
  color: #42b983;
}

.modal-body {
  margin: 20px 0;
}

.modal-default-button {
  float: right;
}

/*
 * The following styles are auto-applied to elements with
 * transition="modal" when their visibility is toggled
 * by Vue.js.
 *
 * You can easily play with the modal transition by editing
 * these styles.
 */

.modal-enter {
  opacity: 0;
}

.modal-leave-active {
  opacity: 0;
}

.modal-enter .modal-container,
.modal-leave-active .modal-container {
  -webkit-transform: scale(1.1);
  transform: scale(1.1);
}

.feedback-textarea {
  width: 400px;
  height: 200px;
}

.input-text {
  width: 300px;
  margin: 10px;
}
</style>

<script>
import Swal from 'sweetalert2';
import HTTP from '../http-common';

export default {
  name: 'FeedbackComponent',
  data() {
    return {
      email: '',
      message: '',
      show: false,
      showSendButton: true,
    };
  },
  methods: {
    send() {
      this.showSendButton = false;
      HTTP
        .post('/feedback', {
          email: this.email,
          message: this.message,
        }, {
          'Content-Type': 'application/json',
        })
        .then(() => {
          Swal.fire({
            icon: 'success',
            title: 'Thanks for your feedback!',
            showConfirmButton: false,
            timer: 2000,
          });
        })
        .catch(() => {
          Swal.fire({
            icon: 'error',
            title: 'Could not send feedback. \nWrite me a mail: info@aero-offers.com',
            showConfirmButton: true,
          });
        });
      this.show = false;
      this.showSendButton = true;
    },
  },
};
</script>
