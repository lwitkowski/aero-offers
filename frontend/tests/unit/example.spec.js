import { mount } from '@vue/test-utils';
import Offers from '../../src/views/Offers.vue';
import { HTTP, setHTTPInstance } from '../../src/http-common.js';

describe('Offers.vue', () => {
  it('offset is increased after fetching data', () => {
    let urlCalledInitially = undefined;
    setHTTPInstance({
      get: jest.fn((url) => {
        urlCalledInitially = url;
        return Promise.resolve({ data: {} });
      })
    });
    const wrapper = mount(Offers);
    expect(wrapper.vm.offset).toBe(30);
    expect(urlCalledInitially).toContain('&offset=0');
  });
});
